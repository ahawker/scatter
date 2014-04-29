"""

"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'


from scatter.tests import ScatterTestCase


class TestStateMachine(ScatterTestCase):
    """
    """

    pass



# class TestStateMachine(unittest.TestCase):
#     """
#
#     """
#
#     def test_something(self):
#
#         from
#
#
#         xx = None
#
#         #pass
#



def main():


    from scatter.state import StateMachine, transition

    class LightBulb(StateMachine):

        @transition('off', 'on')
        def on(self):
            print 'Turning on!'

        @on.on_enter
        def on_enter(self):
            print "Please don't, I'm afraid of the dark!"

        @transition('on', 'off')
        def off(self):
            print 'Turning off!'

        @off.on_exit
        def off_exit(self):
            print "Whew, that's much better!"




    class Human(StateMachine):

        @transition('alive', 'dead')
        def shot(self):
            print 'Someone shot me!'

        @transition('dead', 'alive')
        def revive(self):
            print "It's a miracle!"


    bulb = LightBulb('off')

    #bulb.off()
    bulb.on()
    bulb.off()

    #print LightBulb.transitions


    human = Human('alive')
    human.shot()
    human.revive()
    human.shot()

    #print Human.transitions


    #print StateMachine
    #print StateMachine.transitions

    #for k, v in StateMachine.transitions.iteritems():
    #    print '{0} -- {1}'.format(k, v)


if __name__ == '__main__':
    main()