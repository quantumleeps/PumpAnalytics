import numpy as np
import pint
import copy

u = pint.UnitRegistry()
u.setup_matplotlib(True)
u.define('meter_H2O = 100*cmH2O = mH2O')

units_metric = {
            'N': 'kilowatt',
            'q': 'meter**3/hour',
            'h': 'meter_H2O',
            'e': 'dimensionless'
}
units_US = {
            'N': 'horsepower',
            'q': 'gallon/minute',
            'h': 'foot_H2O',
            'e': 'dimensionless'
}

def check_units(a,b,n):
    return len([1 for x in a if x in b]) == n

def return_remaining_unit(a,b):
    return [x for x in b if x not in a][0]

class PumpCondition:
    def __init__(self, name):
        self.name = name
        self.curve_data = []
        self.units = units_US
        self.duty_point = {}
        self.dp_label = None

    def add_curve_point(self, p):
        n = {}
        units = ['h', 'e', 'q', 'N', 's', 'n']
        required_units = ['s', 'n']
        if (check_units(p, units, 5)) & (check_units(p, required_units, 2)):
            n['s'] = p['s']
            n['n'] = p['n']
            n['N'] = p['N'].to(self.units['N']) if 'N' in p else 0
            n['e'] = p['e'].to_reduced_units() if 'e' in p else 0
            n['h'] = p['h'].to(self.units['h']) if 'h' in p else 0
            n['q'] = p['q'].to(self.units['q']) if 'q' in p else 0
            if return_remaining_unit(p, units) == 'q':
                n['q'] = (p['N']*p['e']/(p['h']*p['s'])).to(self.units['q'])
            elif return_remaining_unit(p, units) == 'h':
                n['h'] = (p['N']*p['e']/(p['q']*p['s'])).to(self.units['h'])
            elif return_remaining_unit(p, units) == 'e':
                n['e'] = (p['h']*p['q']*p['s']/p['N']).to_reduced_units()
            elif return_remaining_unit(p, units) == 'N':
                n['N'] = (p['h']*p['q']*p['s']/p['e']).to(self.units['N'])
        else:
            print(return_remaining_unit(p, units))
        self.curve_data.append(n)
        
    def ready_curve_for_plotting(self):
        q = np.array([])
        h = np.array([])
        e = np.array([])
        N = np.array([])
        for x in self.curve_data:
            q = np.append(q, x['q'].to_base_units().magnitude)
            h = np.append(h, x['h'].to_base_units().magnitude)
            e = np.append(e, x['e'].to_base_units().magnitude)
            N = np.append(N, x['N'].to_base_units().magnitude)
        return {
            'q': (q*u.meter**3/u.second).to(self.units['q']),
            'h': (h*u.kilogram/(u.meter*u.second**2)).to(self.units['h']),
            'e': e*u.dimensionless,
            'N': (N*u.kilogram*u.meter**2/u.second**3).to(self.units['N'])
        }

    def show_curves(self):
        print(self.curve_data)
        
    def change_conditions(self, n_new, s_new):
        selfcopy = copy.deepcopy(self)  
        for a in selfcopy.curve_data:
            a['q'] = a['q']*(n_new/a['n'])
            a['h'] = a['h']*(n_new/a['n'])**2
            a['N'] = (s_new*u.dimensionless/a['s'])*a['N']*(n_new/a['n'])**3
            a['e'] = (a['h']*a['q']*s_new*u.dimensionless/a['N']).to_reduced_units()
            a['s'] = s_new*u.dimensionless
            a['n'] = n_new
        return selfcopy

    def calc_h(self, q):
        a = self.ready_curve_for_plotting()
        uq = a['q'].units
        uh = a['h'].units
        q_norm = q.to(uq)
        q_max = max(a['q'].magnitude)
        if q_norm.magnitude > q_max:
            print('out of range')
            return min(a['h'].magnitude)*uh
        else:
            polyh = np.polyfit(a['q'].magnitude, a['h'].magnitude, 4)
            polyhz = np.poly1d(polyh)
            return polyhz(q_norm.magnitude)*uh

    def calc_e(self, q):
        a = self.ready_curve_for_plotting()
        uq = a['q'].units
        ue = a['e'].units
        q_norm = q.to(uq)
        q_max = max(a['q'].magnitude)
        if q_norm.magnitude > q_max:
            print('out of range')
            return 0*ue
        else:
            polye = np.polyfit(a['q'].magnitude, a['e'].magnitude, 4)
            polyez = np.poly1d(polye)
            return polyez(q_norm.magnitude)*ue

    def calc_N(self, q):
        a = self.ready_curve_for_plotting()
        uq = a['q'].units
        uN = a['N'].units
        q_norm = q.to(uq)
        q_max = max(a['q'].magnitude)
        if q_norm.magnitude > q_max:
            print('out of range')
            return 0*uN
        else:
            polyN = np.polyfit(a['q'].magnitude, a['N'].magnitude, 4)
            polyNz = np.poly1d(polyN)
            return polyNz(q_norm.magnitude)*uN

    def find_duty_point(self, q_desired, h_desired, dp_label=None):
        if not dp_label == None:
            self.dp_label = dp_label
        (q_desired, h_desired)
        uh = self.curve_data[0]['h'].units
        h_desired_norm = h_desired.to(uh)
        h_calculated = self.calc_h(q_desired) #units driven by self
        k = (h_desired_norm.magnitude/h_calculated.magnitude)**0.5 #unitless
        n = self.curve_data[0]['n']*k #units driven by self
        s = self.curve_data[0]['s'] #units driven by self
        new = self.change_conditions(n, s) #units driven by self
        h_calculated = new.calc_h(q_desired)
        count = 0
        while abs(h_calculated.magnitude - h_desired_norm.magnitude) > 1:
            count += 1
            if (h_calculated.magnitude - h_desired_norm.magnitude) > 0:
                n = n - 1*u.revolutions_per_minute
            else:
                n = n + 1*u.revolutions_per_minute
            new = self.change_conditions(n, s)
            h_calculated = new.calc_h(q_desired)
            if count > 5000:
                break
        while abs(h_calculated.magnitude - h_desired_norm.magnitude) > 0.1:
            count += 1
            if (h_calculated.magnitude - h_desired_norm.magnitude) > 0:
                n = n - 0.1*u.revolutions_per_minute
            else:
                n = n + 0.1*u.revolutions_per_minute
            new = self.change_conditions(n, s)
            h_calculated = new.calc_h(q_desired)
            if count > 5000:
                break
        while abs(h_calculated.magnitude - h_desired_norm.magnitude) > 0.01:
            count += 1
            if (h_calculated.magnitude - h_desired_norm.magnitude) > 0:
                n = n - 0.01*u.revolutions_per_minute
            else:
                n = n + 0.01*u.revolutions_per_minute
            new = self.change_conditions(n, s)
            h_calculated = new.calc_h(q_desired)
            if count > 5000:
                break
        while abs(h_calculated.magnitude - h_desired_norm.magnitude) > 0.001:
            count += 1
            if (h_calculated.magnitude - h_desired_norm.magnitude) > 0:
                n = n - 0.001*u.revolutions_per_minute
            else:
                n = n + 0.001*u.revolutions_per_minute
            new = self.change_conditions(n, s)
            h_calculated = new.calc_h(q_desired)
            if count > 5000:
                break
        print('final n: {:.2f}'.format(n))
        print('final q: {:.2f}'.format(q_desired))
        print('final h: {:.2f}'.format((new.calc_h(q_desired)).to(h_desired.units)))
        print('final e: {:.4f}'.format(new.calc_e(q_desired)))
        print('final N: {:.2f}'.format(new.calc_N(q_desired)))
        print('count: {}'.format(count))
        new.duty_point = {
            'q': q_desired,
            'h': new.calc_h(q_desired),
            'e': new.calc_e(q_desired),
            'N': new.calc_N(q_desired),
        }
        return new




        # # print(new.curve_data[0]['n'])
        # h1 = (new.calc_h(q_desired.magnitude))*h_desired.units
        # # print(h1)
        # print('h0: {}'.format(h_calculated))
        # print('n0: {}'.format(self.curve_data[0]['n']))
        # print('h1: {}'.format(h1))
        # print('n1: {}'.format(new.curve_data[0]['n']))
