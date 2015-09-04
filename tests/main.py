"""

"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'


import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
#logger = logging.getLogger(__name__)
logging.warning('FUCK')
#print 'fuck'
#logging.error('FUCK')


#import scatter
#from scatter.ext.zmq import IOLoopService, ChannelService, StreamService

#
# def factory():
#     app = scatter.Scatter()
#     print app.config
#
#     ioloop = IOLoopService()
#
#
#     channel = ChannelService()
#
#
#
#     stream = StreamService()
#     channel.attach(stream)
#
#
#
#     ioloop.attach(channel)
#
#
#     app.attach(ioloop)
#
#     return app


def main2():

    #
    # class Obj(object):
    #     config = None
    #     def init(self, conf):
    #         self.config = conf
    #         print self.config
    #         self.config['NAME'] = 'OBJ'
    #
    # class Thing(object):
    #     child = None
    #     config = None
    #     def __init__(self):
    #         self.config = dict()
    #         self.config['NAME'] = 'THING'
    #         self.config['OBJ'] = dict()
    #         print self.config
    #         self.child = Obj()
    #         self.child.init(self.config['OBJ'])
    #         print 'after'
    #         print self.config
    #
    #
    # t = Thing()
    #


    from scatter.process import Process, Daemon
    import time

    #from scatter.ext.async import AsyncService

    with Process.new() as p:
        #time.sleep(10)
        p.log.error('Hello there!')
        time.sleep(5)

        p.log.error('DONE')
        p.join(1)
        #time.sleep(2)

    #time.sleep(5)


    #p = Process()
    #print p
    #p.start()
    #import time
    ##time.sleep(2)
    #p.stop()
    #print p




def main():
    pass
    #from scatter.ext.gevent import GeventQueue
    # from scatter.ext.gevent import GeventService
    #
    # #xxx = GeventService()
    #
    # import time
    # import gevent
    #
    # def func(log, i):
    #     log.info('~~{0}~~~~~~~~~~~~~~~~~~~'.format(i))
    #     #gevent.sleep(0.5)
    #
    # #def f():
    #
    # with GeventService.new(name='app', config=dict(DEBUG=True)) as service:
    #     service.log.info('app running!!!')
    #     for i in xrange(0, 10000):
    #         service.spawn(func, service.log, i)
    #         gevent.sleep(0)
    #
    #     #service.join(3)
    #     #service.spawn(func, x=1, y=2)
    #     gevent.sleep(5)
    #
    #     import time
    #     #gevent.sleep(10)
    #         # import gevent
    #         # print 'GeventService running...'
    #         # gevent.sleep(1)
    #         # print 'starting job...'
    #         # def func():
    #         #     gevent.sleep(1)
    #         #     return 42
    #         # future = service.spawn(func)
    #         # gevent.sleep(5)
    #         # print future
    #         # print future.get()
    #
    # #import gevent
    #
    # #f()
    #xxx = gevent.spawn(f)
    #xxx.join(10)

        #xxx = service.spawn(func)
        #print xxx
        #import gevent
        #gevent.sleep(3)
        #time.sleep(3)


    #print Queue
    #print QueueService
    # app = factory()
    #
    #
    # def func():
    #     #import time
    #     #time.sleep(1)
    #     print 'func'
    #
    #     #gevent.sleep(0)
    #     print 'stop'
    #     app.stop()
    #
    # #import threading
    # #t = threading.Thread(target=func)
    # #t.start()
    # #t = gevent.spawn(func)
    #
    # #gevent.sleep(0)
    # #t.start()
    #
    # print 'bef run'
    # app.run(10)
    # print 'after run'





if __name__ == '__main__':
    main2()