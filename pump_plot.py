import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

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
unit_mapper = {
    'meter_H2O': 'TDH (meters)',
    'foot_H2O': 'TDH (feet)',
    'gallon/minute': 'Flowrate (USGPM)',
    'meter**3/hour': 'Flowrate (m^3/hr)',
    'horsepower': 'Power (hp)',
    'kilowatt': 'Power (kW)',
    'dimensionless': 'Efficiency',
    'megawatt': 'Power (mW)',
    'meter**3/second': 'Flowrate (m^3/s)',
    'btu/hour': 'Power (BTU/hr)',
    'hogshead/fortnight': 'Flowrate (hogshead/fortnight)'
}

def make_polyfit(x,y,n,e):
    z = np.polyfit(x,y,e)
    p = np.poly1d(z)
#     x_ = np.linspace(min(x), max(x), num=n)
    x_ = np.linspace(min(x), max(x), num=n)
    y_ = p(x_)
    return [x_, y_]

class PumpPlot:
    def __init__(self, name, units=units_US, show_test_dots=True, efficiency_colorbar=False):
        self.name = name
        self.pump_conditions = []
        self.units = units
        self.show_test_dots = show_test_dots
        self.efficiency_colorbar = efficiency_colorbar

    def add_condition(self, condition):
        self.pump_conditions.append(condition)

    def all_curves(self, title, save_location):
        plt.figure()
        fig, ax = plt.subplots(3)
        fig.suptitle(title)
        fig.subplots_adjust(hspace=0.1)
        fig.set_size_inches(8.5, 11)
        for b in self.pump_conditions:
            a = b.ready_curve_for_plotting()
            q_ = ((make_polyfit(a['q'], a['h'], 1000, 4)[0])*a['q'].units).to(self.units['q'])
            e_ = ((make_polyfit(a['q'], a['e'], 1000, 4)[1])*a['e'].units).to(self.units['e'])
            h_ = ((make_polyfit(a['q'], a['h'], 1000, 4)[1])*a['h'].units).to(self.units['h'])
            N_ = ((make_polyfit(a['q'], a['N'], 1000, 4)[1])*a['N'].units).to(self.units['N'])
            if self.efficiency_colorbar:
                ax[0].scatter(q_,h_, c=cm.RdYlGn(np.abs(e_**(3/2))), edgecolor='none')
            else:
                ax[0].plot(q_, h_)
            if self.show_test_dots:
                ax[0].scatter(a['q'].to(self.units['q']), a['h'].to(self.units['h']))
            if 'h' in b.duty_point.keys():
                ax[0].scatter([(b.duty_point['q']).to(self.units['q'])],[(b.duty_point['h']).to(self.units['h'])], s=[1000], marker="+", c="black")
            ax[1].plot(q_, e_)
            if self.show_test_dots:
                ax[1].scatter(a['q'].to(self.units['q']), a['e'].to(self.units['e']))
            if 'e' in b.duty_point.keys():
                ax[1].scatter([b.duty_point['q'].to(self.units['q'])],[b.duty_point['e'].to(self.units['e'])], s=[1000], marker="+", c="black")
            ax[2].plot(q_, N_)
            if self.show_test_dots:
                ax[2].scatter(a['q'].to(self.units['q']), a['N'].to(self.units['N']))
            if 'N' in b.duty_point.keys():
                ax[2].scatter([b.duty_point['q'].to(self.units['q'])],[b.duty_point['N'].to(self.units['N'])], s=[1000], marker="+", c="black")

        ylbl = ax[0].yaxis.get_label()
        ax[0].set_ylabel(unit_mapper[ylbl.get_text()])
        ax[0].set_xlabel('')
        ax[0].grid(True)
        ax[0].minorticks_on()
        ax[0].grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        ylbl = ax[1].yaxis.get_label()
        ax[1].set_ylabel(unit_mapper[ylbl.get_text()])
        ax[1].set_xlabel('')
        ax[1].grid(True)
        vals = ax[1].get_yticks()
        ax[1].set_yticklabels(['{:,.0%}'.format(x) for x in vals])
        ax[1].grid(True)
        ax[1].minorticks_on()
        ax[1].grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        ylbl = ax[2].yaxis.get_label()
        ax[2].set_ylabel(unit_mapper[ylbl.get_text()])
        ax[2].grid(True)
        ax[2].grid(True)
        ax[2].minorticks_on()
        ax[2].grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        fig.tight_layout(pad=3)
        fig.savefig(save_location, dpi=300)

    def h_curve(self, title, save_location):
        plt.figure()
        fig, ax = plt.subplots(1)
        fig.suptitle(title)
        fig.subplots_adjust(hspace=0.1)
        fig.set_size_inches(11, 6)
        for b in self.pump_conditions:
            a = b.ready_curve_for_plotting()
            q_ = ((make_polyfit(a['q'], a['h'], 1000, 4)[0])*a['q'].units).to(self.units['q'])
            e_ = ((make_polyfit(a['q'], a['e'], 1000, 4)[1])*a['e'].units).to(self.units['e'])
            h_ = ((make_polyfit(a['q'], a['h'], 1000, 4)[1])*a['h'].units).to(self.units['h'])
            N_ = ((make_polyfit(a['q'], a['N'], 1000, 4)[1])*a['N'].units).to(self.units['N'])
            if self.efficiency_colorbar:
                ax.scatter(q_,h_, c=cm.RdYlGn(np.abs(e_**(3/2))), edgecolor='none', zorder=1)
            else:
                ax.plot(q_, h_)
            if self.show_test_dots:
                ax.scatter(a['q'].to(self.units['q']), a['h'].to(self.units['h']))
            if 'h' in b.duty_point.keys():
                ax.scatter([(b.duty_point['q']).to(self.units['q'])],[(b.duty_point['h']).to(self.units['h'])], s=[1000], marker="+", c="black", zorder=2)

        ylbl = ax.yaxis.get_label()
        ax.set_ylabel(unit_mapper[ylbl.get_text()])
        # ax.set_xlabel('')
        ax.grid(True)
        ax.minorticks_on()
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        fig.tight_layout(pad=3)
        fig.savefig(save_location, dpi=300)
