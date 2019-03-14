import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.colors as colors
from matplotlib.path import Path
from matplotlib.patches import PathPatch
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

font = {
    "family": "serif",
    "horizontalalignment": "center",
    "verticalalignment": "center",
    "color": "white",
    "size": 11
}

def make_polyfit(x,y,n,e):
    z = np.polyfit(x,y,e)
    p = np.poly1d(z)
#     x_ = np.linspace(min(x), max(x), num=n)
    x_ = np.linspace(min(x), max(x), num=n)
    y_ = p(x_)
    return [x_, y_]

def add_duty_point_triangle(x, y, s, fontdict, axis, fh, fv):
    h = (axis.get_xlim()[1] - axis.get_xlim()[0])/fh
    v = (axis.get_ylim()[1] - axis.get_ylim()[0])/fv
    path = Path([[x, y], [x-h, y], [x, y-v], [x, y]])
    patch = PathPatch(path, facecolor='black', edgecolor='white')
    axis.add_patch(patch)
    axis.text(x - h/3.8, y - v/3, s, fontdict=fontdict, zorder=3)

class PumpPlot:
    def __init__(self, name, units=units_US, show_test_dots=True, efficiency_colorbar=False, color_map_type='spring'):
        self.name = name
        self.pump_conditions = []
        self.units = units
        self.show_test_dots = show_test_dots
        self.efficiency_colorbar = efficiency_colorbar
        self.color_map_type = color_map_type

    def add_condition(self, condition):
        self.pump_conditions.append(condition)

    def all_curves(self, title, save_location):
        counter = 1
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
                ax[0].scatter(q_,h_, c=e_, norm=colors.PowerNorm(gamma=3.1), cmap=self.color_map_type, edgecolor='none')
            else:
                ax[0].plot(q_, h_)
            if self.show_test_dots:
                ax[0].scatter(a['q'].to(self.units['q']), a['h'].to(self.units['h']))
            if 'h' in b.duty_point.keys():
                x = ((b.duty_point['q']).to(self.units['q'])).magnitude
                y = ((b.duty_point['h']).to(self.units['h'])).magnitude
                if not b.dp_label == None:
                    add_duty_point_triangle(x, y, b.dp_label, font, ax[0], 14, 9)
                else:
                    add_duty_point_triangle(x, y, counter, font, ax[0], 14, 9)
                    counter += 1
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

    def h_curve(self, title, save_location, custom_colorbar_ticks=None):
        counter = 1
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
                colorcurve = ax.scatter(q_,h_, c=e_, norm=colors.PowerNorm(gamma=3.1), cmap=self.color_map_type, edgecolor='none', zorder=1)
            else:
                ax.plot(q_, h_)
            if self.show_test_dots:
                ax.scatter(a['q'].to(self.units['q']), a['h'].to(self.units['h']))
            if 'h' in b.duty_point.keys():
                x = ((b.duty_point['q']).to(self.units['q'])).magnitude
                y = ((b.duty_point['h']).to(self.units['h'])).magnitude
                if not b.dp_label == None:
                    add_duty_point_triangle(x, y, b.dp_label, font, ax, 14, 12)
                else:
                    add_duty_point_triangle(x, y, counter, font, ax, 14, 12)
                    counter += 1

        ylbl = ax.yaxis.get_label()
        ax.set_ylabel(unit_mapper[ylbl.get_text()])
        # ax.set_xlabel('')
        ax.grid(True)
        ax.minorticks_on()
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        
        if not custom_colorbar_ticks == None:
            cbar = fig.colorbar(mappable=colorcurve, ticks=custom_colorbar_ticks)
        else:
            cbar = fig.colorbar(mappable=colorcurve)
        cbar.ax.get_yaxis().labelpad = 15
        cbar.ax.set_ylabel('Efficiency', rotation=270)
        fig.tight_layout(pad=3)
        fig.savefig(save_location, dpi=300)
