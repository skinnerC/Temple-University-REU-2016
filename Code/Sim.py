import simpy
import random
from operator import itemgetter
import numpy
#import matplotlib.pyplot as plt
#from matplotlib import font_manager

#plt.style.use('seaborn-whitegrid')
running = True
results = None
#diff = []

class Cache:
    def __init__(self, env, id_, lambda_, mu, debug, gen_update_time, gen_processing_time):
#        print 'Cache {0} has a mu of {1}'.format(id_, mu)
        self.env = env
        self.id_ = id_
        self.lambda_ = lambda_
        self.mu = mu
        self.debug = debug
        
        self.timestamp = 0.0
        self.sent_timestamp = 0.0
        
        self.processing_time = 0.0
        
        self.gen_update_time = gen_update_time
        self.gen_processing_time = gen_processing_time
        
#        # Age graph
#        self.time = [0]
#        self.age = [0]
#        self.sent_time = []
#        self.request_time = []
#        self.pro_time = []

        # Start simulation of file updates
        self.action = self.env.process(self.run())

    def run(self):
        
        # Update file each time a new file is generated
        while running:
            wait = self.gen_update_time(self.lambda_)
            
            yield self.env.timeout(wait)
#            print 'I updated\t{0}\t{1}'.format(wait, self.env.now)
            self.timestamp = self.env.now
#            self.age += [wait]
#            self.time += [self.timestamp]
#            self.age += [0]
#            self.time += [self.timestamp]
            if self.debug: print 'Time {0}: Cache {1} updated its\' file'.format(self.timestamp, self.id_)
        
#        fig = plt.figure()
#        ax = fig.add_subplot(1,1,1, axisbg = 'w')
#        ax.plot(self.time, self.age)
##        for i in self.request_time:
##            ax.axvline(x=i, color='k', ls='dashed')
##        for i in self.sent_time:
##            ax.axvline(x=i, color='r', ls='dashed')
#        font = {'fontname':'Times New Roman', 'weight':'bold'}
#        tick_font = font_manager.FontProperties(family='Times New Roman', size=28)
#        for label in ax.xaxis.get_ticklabels() + ax.yaxis.get_ticklabels():
#            label.set_fontproperties(tick_font)
#        ax.set_xlim([0, self.time[-1]])
#        ax.set_title('Age of Information Over Time', size = 34, **font)
#        ax.set_xlabel('Time', size = 34, **font)
#        ax.set_ylabel('Age of Information', size = 34, **font)
#        plt.tight_layout()
##        plt.savefig('Age_Cache{0}_{1}.pdf'.format(self.id_, hex(id(self))), bbox_inches='tight')
#        plt.show()
            
    def send_file(self):
        # Send current file
#        self.pro_time += [self.processing_time]
#        self.sent_time += [self.env.now]
        self.sent_timestamp = self.timestamp
        yield self.env.timeout(self.processing_time)
#        self.sent_time += [self.env.now]
#        self.sent_timestamp = self.timestamp
        
        if self.debug: print '\t\tTime {0}: Recieved file from Cache {1} (generated at time {2})'.\
        format(self.env.now, self.id_, self.sent_timestamp)
    
    def generate_processing_time(self):
#        self.request_time += [self.env.now]
        
        self.processing_time = self.gen_processing_time(self.mu)
        return self.processing_time
    
class Client:
    def __init__(self, env, d, n, request_count, lambda_, mu, debug, gen_update_time, gen_processing_time, random_mu):
        self.env = env
        self.d = d
        self. n = n
        self.request_count = request_count
        self.debug = debug
        self.index = 0
        
        # Set up Caches
        self.selected_Caches = None
        if random_mu:
            self.Caches = [Cache(env, i, lambda_, random.uniform((.5*mu), (1.5*mu)), debug, gen_update_time, gen_processing_time) for i in range(n)]
        else:
            self.Caches = [Cache(env, i, lambda_, mu, debug, gen_update_time, gen_processing_time) for i in range(n)]
        
        # Start simulation of client
        self.action = self.env.process(self.run())

    def request_file(self):
        # Request file
        # Get the d fastest Caches
        self.selected_Caches = [(Cache.generate_processing_time(), Cache) for Cache in self.Caches]
        self.selected_Caches.sort(key=itemgetter(0))
        trash, self.selected_Caches = zip(*(self.selected_Caches[:self.d]))
        
#        global diff
#        if self.d - 1: diff += [trash[1] - trash[0]]
        # Make the d fastest send their file
        for Cache in self.selected_Caches:
            self.env.process(Cache.send_file())
        
        # Find how long it will take for a all files to reach client
        longest_wait = self.selected_Caches[self.d - 1].processing_time
        
        # Logging messages
        if self.debug: print '\tLongest wait time is ' + str(longest_wait)
        if self.debug: print '\tWaiting for files...'
        
        # Wait for all files to be recieved
        yield self.env.timeout(longest_wait)

    def run(self):
        global results
        global running
        
        running = True
        results = [] 
        
        while self.index < self.request_count:
            # Request file
            if self.debug: print 'Time {}: Requesting files...'.format(self.env.now)
            yield self.env.process(self.request_file())
            
            # Determine which file is the freshest out the ones recieved
            freshest = max(map(lambda Cache: Cache.sent_timestamp, self.selected_Caches))
            if self.debug: print '\tThe freshest file was generated at time {}'.format(freshest)

            # Calculate the age of information of the file recieved            
            age = self.env.now - freshest
            if self.debug: print '\tAge of information: {0}'.format(age)
            
            results += [age]
            self.index += 1
            
        # Stop files from updating / end simulation
        running = False

def simulate(d, n = 5, mu = 0.1, lambda_ = 0.1, request_count = 10, seed = 0, debug = False,
             gen_update_time = random.expovariate, gen_processing_time = random.expovariate, random_mu = False):
    # d = The number of files that you will wait for
    # n = The number of Caches available
    # mu = Effects the exponential distribution of the time it takes for a file to be transmited from Cache to client 
    # lambda_ = Effects the poisson distribution of the time it takes for a file to be transmitted from file source
    # to a Cache
    # request_count = The number of file retrievals the client intends to make
    # seed = Random seed
    # debug = Enables logging

    random.seed(seed)
    numpy.random.seed(seed)

    # Create Simulation Environment and start simulation
    global running
    
    running = True
    env = simpy.Environment()
    client = Client(env, d, n, request_count, lambda_, mu, debug, gen_update_time, gen_processing_time, random_mu)
    env.run()
    
    if debug: print 'Simulation Complete\n'
#    print results
    return sum(results)/len(results)
    

if __name__ == '__main__':
    print simulate(1,n=5,mu=1,lambda_=1, request_count=10, debug=True, gen_processing_time= lambda theta: random.gammavariate(3, theta))
#    print diff
#    if len(diff) != 0 and diff != 0: print sum(diff)/len(diff)