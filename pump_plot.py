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
    'dimensionless': 'Efficiency'
}

def make_polyfit(x,y,n,e):
    z = np.polyfit(x,y,e)
    p = np.poly1d(z)
#     x_ = np.linspace(min(x), max(x), num=n)
    x_ = np.linspace(min(x), max(x), num=n)
    y_ = p(x_)
    return [x_, y_]

class PumpPlot:
    def __init__(self, name):
        self.name = name
        self.pump_conditions = []
        self.units = units_US
        
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
            q_, e_ = make_polyfit(a['q'], a['e'], 1000, 4)
            h_ = make_polyfit(a['q'], a['h'], 1000, 4)[1]
            N_ = make_polyfit(a['q'], a['N'], 1000, 4)[1]
            ax[0].scatter(q_,h_, c=cm.RdYlGn(np.abs(e_**(3/2))), edgecolor='none')
            # ax[0].plot(q_, h_)
            ax[0].scatter(a['q'], a['h'])
            if 'h' in b.duty_point.keys():
                ax[0].scatter([b.duty_point['q']],[b.duty_point['h']], s=[1000], marker="+", c="black")
            ax[1].plot(q_, e_)
            ax[1].scatter(a['q'], a['e'])
            if 'e' in b.duty_point.keys():
                ax[1].scatter([b.duty_point['q']],[b.duty_point['e']], s=[1000], marker="+", c="black")    
            ax[2].plot(q_, N_)
            ax[2].scatter(a['q'], a['N'])
            if 'N' in b.duty_point.keys():
                ax[2].scatter([b.duty_point['q']],[b.duty_point['N']], s=[1000], marker="+", c="black")
    
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
        fig.set_size_inches(11, 8.5)
        for b in self.pump_conditions:
            a = b.ready_curve_for_plotting()
            q_, e_ = make_polyfit(a['q'], a['e'], 1000, 4)
            h_ = make_polyfit(a['q'], a['h'], 1000, 4)[1]
            N_ = make_polyfit(a['q'], a['N'], 1000, 4)[1]
            ax.scatter(q_,h_, c=cm.RdYlGn(np.abs(e_**(3/2))), edgecolor='none')
            # ax[0].plot(q_, h_)
            ax.scatter(a['q'], a['h'])
            if 'h' in b.duty_point.keys():
                ax.scatter([b.duty_point['q']],[b.duty_point['h']], s=[1000], marker="+", c="black")

        ylbl = ax.yaxis.get_label()
        ax.set_ylabel(unit_mapper[ylbl.get_text()])
        # ax.set_xlabel('')
        ax.grid(True)
        ax.minorticks_on()
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        fig.tight_layout(pad=3)
        fig.savefig(save_location, dpi=300)