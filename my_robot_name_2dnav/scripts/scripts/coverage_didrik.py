#!/usr/bin/env python  
 
import roslib;
import rospy  
import actionlib  
from actionlib_msgs.msg import *  
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped, Point, Quaternion, Twist  
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal  
from random import sample  
from math import pow, sqrt  
 
class NavTest():  
    def __init__(self):  
        rospy.init_node('nav_test', anonymous=True)  
 
        rospy.on_shutdown(self.shutdown)  
 
        # How long in seconds should the robot pause at each location?   
        self.rest_time = rospy.get_param("~rest_time", 2)  
 
        # Are we running in the fake simulator?  
        self.fake_test = rospy.get_param("~fake_test", False)  
 
        # Goal state return values  
        goal_states = ['PENDING', 'ACTIVE', 'PREEMPTED',   
                       'SUCCEEDED', 'ABORTED', 'REJECTED',  
                       'PREEMPTING', 'RECALLING', 'RECALLED',  
                       'LOST']  
 
        # Set up the goal locations. Poses are defined in the map frame.    
        # An easy way to find the pose coordinates is to point-and-click  
        # Nav Goals in RViz when running in the simulator.  
        # Pose coordinates are then displayed in the terminal  
        # that was used to launch RViz.  
        locations = dict()  
 
        locations['1'] = Pose(Point(45,600, -12,000, 0,000), Quaternion(0,000, 0,000, 0,000, 1,000))  
        locations['2'] = Pose(Point(60,500, -12,000, 0,000), Quaternion(0,000, 0,000, -0,700, 0,714))  
        locations['3'] = Pose(Point(60,500, -17,000, 0,000), Quaternion(0,000, 0,000, 1,000, 0,000))  
        locations['4'] = Pose(Point(45,600, -17,000, 0,000), Quaternion(0,000, 0,000, 0,710, 0,704)) 
	locations['5'] = Pose(Point(45,600, -12,500, 0,000), Quaternion(0,000, 0,000, -0,010, 1,000))  
        locations['6'] = Pose(Point(60,500, -12,500, 0,000), Quaternion(0,000, 0,000, -0,715, 0,699))  
        locations['7'] = Pose(Point(60,500, -13,500, 0,000), Quaternion(0,000, 0,000, 1,000, -0,007))  
        locations['8'] = Pose(Point(45,600, -13,500, 0,000), Quaternion(0,000, 0,000, -0,710, 0,704)) 
	locations['9'] = Pose(Point(45,600, -14,500, 0,000), Quaternion(0,000, 0,000, -0,003, 1,000))  
        locations['10'] = Pose(Point(60,500, -14,500, 0,000), Quaternion(0,000, 0,000, -0,705, 0,710))  
        locations['11'] = Pose(Point(60,500, -15,500, 0,000), Quaternion(0,000, 0,000, 1,000, 0,002))  
        locations['12'] = Pose(Point(45,600, -15,500, 0,000), Quaternion(0,000, 0,000, -0,711, 0,704))
        locations['13'] = Pose(Point(45,600, -16,500, 0,000), Quaternion(0,000, 0,000, -0,019, 1,000)) 
        locations['14'] = Pose(Point(60,500, -16,500, 0,000), Quaternion(0,000, 0,000, -0,714, 0,701)) 
        locations['15'] = Pose(Point(60,500, -17,000, 0,000), Quaternion(0,000, 0,000, 1,000, 0,002)) 
        locations['16'] = Pose(Point(45,600, -17,000, 0,000), Quaternion(0,000, 0,000, 0,720, 0,693)) 
        locations['17'] = Pose(Point(45,600, -12,000, 0,000), Quaternion(0,000, 0,000, 0,000, 1,000)) 
         
        #locations['midten'] = Pose(Point(-42.651, 24.841, 0.000), Quaternion(0.000, 0.000,-0.734, 0.679))  
        #locations['dining_room_1'] = Pose(Point(-0.861, -0.019, 0.000), Quaternion(0.000, 0.000, 0.892, -0.451))  
 
        # Publisher to manually control the robot (e.g. to stop it)  
        self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist)  
 
        # Subscribe to the move_base action server  
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)  
 
        rospy.loginfo("Waiting for move_base action server...")  
 
        # Wait 60 seconds for the action server to become available  
        self.move_base.wait_for_server(rospy.Duration(60))  
 
        rospy.loginfo("Connected to move base server")  
 
        # A variable to hold the initial pose of the robot to be set by   
        # the user in RViz   
        initial_pose = PoseWithCovarianceStamped()  
 
        # Variables to keep track of success rate, running time,  
        # and distance traveled  
        n_locations = len(locations)  
        n_goals = 0  
        n_successes = 0  
        i = n_locations  
        distance_traveled = 0  
        start_time = rospy.Time.now()  
        running_time = 0  
        location = ""  
        last_location = ""  
 
        # Get the initial pose from the user  
        #rospy.loginfo("*** Click the 2D Pose Estimate button in RViz to set the robot's initial pose...")  
        #rospy.wait_for_message('initialpose', PoseWithCovarianceStamped)  
        #self.last_location = Pose()  
        #rospy.Subscriber('initialpose', PoseWithCovarianceStamped, self.update_initial_pose)  
 
        # Make sure we have the initial pose  
        #while initial_pose.header.stamp == "":  
        #    rospy.sleep(1)  
 
        rospy.loginfo("Starting navigation test")  
 
        # Begin the main loop and run through a sequence of locations  
        while not rospy.is_shutdown():  
            # If we've gone through the current sequence,  
            # start with a new random sequence  
            if i == n_locations:  
                i = 0  
                sequence = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17']
                # Skip over first location if it is the same as  
                # the last location  
                if sequence[0] == last_location:  
                    i = 1 
		print sequence
 
            # Get the next location in the current sequence  
            location = sequence[i]  
 
            # Keep track of the distance traveled.  
            # Use updated initial pose if available.  
            if initial_pose.header.stamp == "":  
                distance = sqrt(pow(locations[location].position.x -   
                                    locations[last_location].position.x, 2) +  
                                pow(locations[location].position.y -   
                                    locations[last_location].position.y, 2))  
            else:  
                rospy.loginfo("Updating current pose.")  
                distance = sqrt(pow(locations[location].position.x -   
                                    initial_pose.pose.pose.position.x, 2) +  
                                pow(locations[location].position.y -   
                                    initial_pose.pose.pose.position.y, 2))  
                initial_pose.header.stamp = ""  
 
            # Store the last location for distance calculations  
            last_location = location  
 
            # Increment the counters  
            i += 1  
            n_goals += 1  
 
            # Set up the next goal location  
            self.goal = MoveBaseGoal()  
            self.goal.target_pose.pose = locations[location]  
            self.goal.target_pose.header.frame_id = 'map'  
            self.goal.target_pose.header.stamp = rospy.Time.now()  
 
            # Let the user know where the robot is going next  
            rospy.loginfo("Going to: " + str(location))  
 
            # Start the robot toward the next location  
            self.move_base.send_goal(self.goal)  
 
            # Allow 5 minutes to get there  
            finished_within_time = self.move_base.wait_for_result(rospy.Duration(300))   
 
            # Check for success or failure  
            if not finished_within_time:  
                self.move_base.cancel_goal()  
                rospy.loginfo("Timed out achieving goal")  
            else:  
                state = self.move_base.get_state()  
                if state == GoalStatus.SUCCEEDED:  
                    rospy.loginfo("Goal succeeded!")  
                    n_successes += 1  
                    distance_traveled += distance  
                    rospy.loginfo("State:" + str(state))  
                else:  
                  rospy.loginfo("Goal failed with error code: " + str(goal_states[state]))  
 
            # How long have we been running?  
            running_time = rospy.Time.now() - start_time  
            running_time = running_time.secs / 60.0  
 
            # Print a summary success/failure, distance traveled and time elapsed  
            rospy.loginfo("Success so far: " + str(n_successes) + "/" +   
                          str(n_goals) + " = " +   
                          str(100 * n_successes/n_goals) + "%")  
            rospy.loginfo("Running time: " + str(trunc(running_time, 1)) +   
                          " min Distance: " + str(trunc(distance_traveled, 1)) + " m")  
            rospy.sleep(self.rest_time)  
 
    def update_initial_pose(self, initial_pose):  
        self.initial_pose = initial_pose  
 
    def shutdown(self):  
        rospy.loginfo("Stopping the robot...")  
        self.move_base.cancel_goal()  
        rospy.sleep(2)  
        self.cmd_vel_pub.publish(Twist())  
        rospy.sleep(1)  
 
def trunc(f, n):  
    # Truncates/pads a float f to n decimal places without rounding  
    slen = len('%.*f' % (n, f))  
    return float(str(f)[:slen])  
 
if __name__ == '__main__':  
    try:  
        NavTest()  
        rospy.spin()  
    except rospy.ROSInterruptException:  
        rospy.loginfo("AMCL navigation test finished.")