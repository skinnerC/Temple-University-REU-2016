import Tkinter as tk
import matplotlib
import matplotlib.pyplot
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import font_manager
from scipy.interpolate import interp1d
import os
import hashlib
import random
import numpy
import Sim

matplotlib.pyplot.style.use('seaborn-whitegrid')

def pareto(x):
    temp = (numpy.random.pareto(x) + 1)
    if x > 1:
        temp *= (x-1)
    else:
        temp *= x
    return 1./temp

class Application(tk.Frame):
    def __init__(self, master):
        if not os.path.isdir('./simulation_results'):
            os.makedirs('./simulation_results')
        
        # Create frame
        tk.Frame.__init__(self, master, width=900, height=800)
        self.master.title('Simulation')
        
        # Configure rows
        self.pack_propagate(0)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)
        self.columnconfigure(8, weight=1)
        self.columnconfigure(9, weight=1)
        self.columnconfigure(10, weight=1)
        
        # Configure graphing area
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
		
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=11, padx=5, pady=5, sticky='NESW')

        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(row = 1, column=0, columnspan=11, sticky='NESW')
        toolbar = NavigationToolbar2TkAgg(self.canvas, toolbar_frame)
        toolbar.update()
        
        # Variable entry boxes
        n_text=tk.StringVar(value = 'n = ')
        n_label=tk.Label(self, textvariable=n_text)
        n_label.grid(row = 2, column = 0, sticky='E')
        
        n_field=tk.StringVar(value = '50')
        self.n=tk.Entry(self, textvariable=n_field, width=10)
        self.n.bind('<Return>', self.update)
        self.n.grid(row = 2, column = 1)
        
        lamba_text=tk.StringVar(value = 'lamda = ')
        lamba_label=tk.Label(self, textvariable=lamba_text)
        lamba_label.grid(row = 2, column = 2, sticky='E')
        
        lamba_field=tk.StringVar(value = '1')
        self.lambda_=tk.Entry(self,textvariable=lamba_field, width=10)
        self.lambda_.bind('<Return>', self.update)
        self.lambda_.grid(row=2, column=3)
        
        mu_text=tk.StringVar(value = 'mu = ')
        mu_label=tk.Label(self, textvariable=mu_text)
        mu_label.grid(row=2, column=4, sticky='E')
        
        mu_field=tk.StringVar(value = '400')
        self.mu=tk.Entry(self,textvariable=mu_field, width=10)
        self.mu.bind('<Return>', self.update)
        self.mu.grid(row=2, column=5)
        
        request_count_text=tk.StringVar(value = 'request count = ')
        request_count_label=tk.Label(self, textvariable=request_count_text)
        request_count_label.grid(row=2, column=6, sticky='E')
        
        request_count_field=tk.StringVar(value = '1000')
        self.request_count=tk.Entry(self,textvariable=request_count_field, width=10)
        self.request_count.bind('<Return>', self.update)
        self.request_count.grid(row=2, column=7)
        
        seed_text=tk.StringVar(value = 'seed = ')
        seed_label=tk.Label(self, textvariable=seed_text)
        seed_label.grid(row=2, column=8, sticky='E')
        
        seed_field=tk.StringVar(value = '0')
        self.seed=tk.Entry(self,textvariable=seed_field, width=10)
        self.seed.bind('<Return>', self.update)
        self.seed.grid(row=2, column=9)
        
        buttontext = tk.StringVar(value = 'Update')
        button = tk.Button(self, textvariable=buttontext, command=self.update)
        button.grid(row=2, column=10, padx=10)
        
        # Settings checkboxes
        self.interpolate = tk.IntVar()
        interpolate_checkbox = tk.Checkbutton(self, text='Interpolate', variable=self.interpolate)
        interpolate_checkbox.grid(row=3, column=4, columnspan=2)
        
        self.random_mu = tk.IntVar()
        random_mu_checkbox = tk.Checkbutton(self, text='Randomize Mu', variable=self.random_mu)
        random_mu_checkbox.grid(row=3, column=6, columnspan=2)
        
        # Distribution selection
        dist_text=tk.StringVar(value = 'Update Distribution')
        dist_label=tk.Label(self, textvariable=dist_text)
        dist_label.grid(row=4, column=3, sticky='NESW', columnspan=3)

        dist_text2 = tk.StringVar(value = 'Processing Time Distribution')
        dist_label2 = tk.Label(self, textvariable=dist_text2)
        dist_label2.grid(row=5, column=3, sticky='NESW', columnspan=3)
        
        self.choices = ['Exponential', 'Power']
        self.distribution = [random.expovariate, numpy.random.power, random.gammavariate]
        
        self.update_dist = tk.StringVar(self)
        self.update_dist.set(self.choices[0])
        update_options = tk.OptionMenu(self, self.update_dist, *self.choices)
        update_options.grid(row=4, column=6, sticky='NESW', columnspan=2)
        
        k_text = tk.StringVar(value = 'k = ')
        k_label = tk.Label(self, textvariable=k_text)
        k_label.grid(row=5, column=8, sticky='E')
        
        k_field = tk.StringVar()
        self.k = tk.Entry(self,textvariable=k_field, width=10)
        self.k.bind('<Return>', self.update_dist)
        self.k.grid(row=5, column=9)
        
        def reveal(option):
            if option == 'Gamma':
                k_label.grid()
                self.k.grid()
            else:
                k_label.grid_remove()
                self.k.grid_remove()
                
        
        self.processing = tk.StringVar(self)
        self.processing.set(self.choices[0])
        processing_options = tk.OptionMenu(self, self.processing, *(self.choices+['Gamma']), command=reveal)
        processing_options.grid(row=5, column=6, sticky='NESW', columnspan=2)
        
        # Variable information        
        info_string = '''d = The number of files to wait for
        n = The number of Caches available
        mu = Effects the processing time distribution (the time it takes for a file to be transmited from Cache to client) 
        lambda = Effects the update time distribution (the time it takes for a file to be transmitted from file source to a Cache)
        request count = The number of file retrievals the client intends to make
        seed = Random seed '''
        info = tk.Label(self, text=info_string)
        info.grid(row=6, columnspan=11)       
        
        # Show application
        reveal(self.choices[0])
        self.pack(fill='both', expand='yes')
        
    def update(self, event=None):
        # Get parameters
        n = int(self.n.get())
        mu = float(self.mu.get())
        lambda_ = float(self.lambda_.get())
        request_count = int(self.request_count.get())
        seed = int(self.seed.get())
        update_func = self.distribution[self.choices.index(self.update_dist.get())]
        rand_mu = self.random_mu.get()
        
        # Pick processing distribution
        if self.processing.get() != 'Gamma':
            processing_dist = self.distribution[self.choices.index(self.processing.get())]
        else:
            k = int(self.k.get())
            processing_dist = lambda theta: random.gammavariate(k, theta)
        
        # Generate hash for results
        filename = '{0}-{1}-{2}-{3}-{4}-{5}-{6}-{7}'.format(n, mu, lambda_, request_count, seed, self.update_dist.get(), self.processing.get(), rand_mu)
        hasher = hashlib.md5(filename.encode())
        filename = hasher.hexdigest() + filename.replace('-', '') + '.txt'
        
        x = [d for d in range(1, n+1)] #51
        
        # If any results match the generated hash pull those reults
        if not os.path.isfile('./simulation_results/'+filename):
            # else run simulation
            y = [Sim.simulate(d, n=n, mu=mu, lambda_=lambda_, request_count=request_count, seed=seed, debug=False,
                              gen_update_time = update_func, gen_processing_time = processing_dist, random_mu=rand_mu)
                for d in range(1, n+1)] #51
            
            with open('./simulation_results/'+filename, 'w') as f:
                for i in y: 
                    f.write('{}\n'.format(i))
        else:
            with open('./simulation_results/'+filename, 'r') as f:
                y = [float(line.strip()) for line in f]
        
        # Interpolate data if option is selected
        if self.interpolate.get():
            new_x = [i/10.0 for i in range(10, (n*10)+1, 1)]
            new_y = interp1d(x, y, kind = 'cubic')(new_x)
        
        # Plot data data
        self.ax.clear()
        
        if self.interpolate.get():
            self.ax.plot(new_x, new_y)
            self.ax.set_ylim([0, max(new_y)*1.1])
        else:
            self.ax.plot(x, y)
            self.ax.set_ylim([0, max(y)*1.1])
            
        self.ax.set_xlim([1, n])
        self.ax.xaxis.set_ticks(x)
        
        for x, label in enumerate(self.ax.xaxis.get_ticklabels()):
            if (x + 1) % 5 != 0 and x != 0:
                label.set_visible(False)
        
        font = {'fontname':'Times New Roman', 'weight':'bold'}
        tick_font = font_manager.FontProperties(family='Times New Roman', size=24)
        for label in self.ax.xaxis.get_ticklabels() + self.ax.yaxis.get_ticklabels():
            label.set_fontproperties(tick_font)
        
        self.ax.set_title('Average Age vs Responses Received', size=30, y = 1.04, **font)
        self.ax.set_xlabel('Responses Received', size = 30, **font)
        self.ax.set_ylabel('Average Age', size = 30, **font)
        self.fig.tight_layout()
        self.canvas.show()
    
    def run(self):
        self.mainloop()

if __name__ == '__main__':
    app = Application(tk.Tk())
    app.run()