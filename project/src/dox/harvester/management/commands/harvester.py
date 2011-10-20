from django.core.management.base import NoArgsCommand
from dox.harvester.spider import Spider




class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        #test spider run
        
        robot = Spider('django')
        robot.harvest()
        
        f = open("test_harvest.xml", "wt")
        f.write(robot.xml())
        f.close()
