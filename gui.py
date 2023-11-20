import cv2
import pygame
from pygame.locals import *
import os
import sys
from ui_utils import *
import tkinter
import tkinter.filedialog
from findCoordinateTransformationMatrix import *
from convert_2d_to_3d import *
from combine import combine
from utils import *
import pickle
import re

tetha = (0,0,0)
tetha_x = 0

def rotation_x(tetha):
    tetha= np.radians(tetha)
    return [[1,0,0],[0,np.cos(tetha),-np.sin(tetha)],[0,np.sin(tetha),np.cos(tetha)]]
def rotation_y(tetha):
    tetha= np.radians(tetha)
    return [[np.cos(tetha),0,np.sin(tetha)],[0,1,0],[-np.sin(tetha),0,np.cos(tetha)]]
def rotation_z(tetha):
    tetha= np.radians(tetha)
    return [[np.cos(tetha),-np.sin(tetha),0],[np.sin(tetha),np.cos(tetha),0],[0,0,1]]


connections = [[15, 13], [13, 11], [16, 14], [14, 12],
               [5, 11], [11, 12], [12, 6], [6, 5],
               [5, 7], [7, 9], [6, 8], [8, 10],
               [3, 1], [1, 0], [0, 2], [2, 4]]

pose_limb_color = ['hand1', 'hand1', 'hand2', 'hand2', 'body', 'body', 'body', 'body', 'foot1', 'foot1', 'foot2',
                   'foot', 'head', 'head', 'head', 'head']


colors = [(0,0,255), (0,0,0), 'green', 'blue']
                   
class App:
    def __init__(self) -> None:
        self.step = 0
        w = screen.get_width()
        h = screen.get_height()
        self.menu_jarvis_btn = Button("Opne JARVIS", w/3, h/10, (w//3, (h-3*h//10-2*h//30)//2), func=self.__open_jarvis)
        self.menu_calibration_btn = Button("3D transformation", w/3, h/10, (w//3, (h-3*h//10-2*h//30)//2+h//10+h//30), func=self.__select_option, option=1)
        self.menu_visualization_btn = Button("3D localization", w/3, h/10, (w//3, (h-3*h//10-2*h//30)//2+2*(h//10+h//30)), func=self.__select_option, option=11)

        self.tetha_x = -20
        self.tetha_y = -30
        self.tetha_z = 0
        offset_x = w//50
        self.project_name_lbl = Label(offset_x, 20, 100, 50, text="Camera Pair Name:")
        self.project_name_inp = InputBox(offset_x, 70, 200, 50, func=self.__set_project_name)
        self.cube_width = 2500
        self.cube_height = 1200
        self.cube_depth = 4500
        self.width_lbl = Label(offset_x, h//5, 100, 30, text="room width (mm):")
        self.width_inp = InputBox(offset_x, h//5+50, 100, 50, text=str(self.cube_width) ,func=self.__change_width)
        self.height_lbl = Label(offset_x+11*w//100, h//5, 100, 30, text="room height (mm):")
        self.height_inp = InputBox(offset_x+11*w//100, h//5+50, 100, 50, text=str(self.cube_height) ,func=self.__change_height)
        self.depth_lbl = Label(offset_x+2*11*w//100, h//5, 100, 30, text="room depth (mm):")
        self.depth_inp = InputBox(offset_x+2*11*w//100, h//5+50, 100, 50, text=str(self.cube_depth) ,func=self.__change_depth)
        self.primary_lbl = Label(offset_x, 4*h//10, 100, 50, text="Primary Camera:")
        self.name_lbl_1 = Label(offset_x, 4*h//10+50, 50, 30, text="name:")
        self.name_inp_1 = InputBox(offset_x, 4*h//10+100, 100, 50,func=self.__set_camera_name, cam=1)
        self.wall_lbl_1 = Label(offset_x+12*w//125, 4*h//10+50, 100, 30, text="select wall:")
        wall_icon = np.full((30,30,4), (255,255,0,50), np.uint8)
        wall_selected_icon = np.full((30,30,4), (50,50,50,200), np.uint8)
        wall_selected_icon[5:26,5:26] = (255,255,0,200)
        self.wall1_btn_1 = ImageButton(wall_icon, wall_selected_icon, 30, 30, (offset_x+12*w//125, 4*h//10+100), func=self.__select_wall1, cam=1)
        wall_icon = np.full((30,30,4), (0,255,0,50), np.uint8)
        wall_selected_icon[5:26,5:26] = (0,255,0,200)
        self.wall2_btn_1 = ImageButton(wall_icon, wall_selected_icon, 30,30,(offset_x+12*w//125+50,4*h//10+100), func=self.__select_wall2, cam=1)
        wall_icon = np.full((30,30,4), (0,0,255,50), np.uint8)
        wall_selected_icon[5:26,5:26] = (0,0,255,200)
        self.wall3_btn_1 = ImageButton(wall_icon, wall_selected_icon, 30,30,(offset_x+12*w//125,4*h//10+100+50), func=self.__select_wall3, cam=1)
        wall_icon = np.full((30,30,4), (255,0,0,50), np.uint8)
        wall_selected_icon[5:26,5:26] = (255,0,0,200)
        self.wall4_btn_1 = ImageButton(wall_icon, wall_selected_icon, 30,30,(offset_x+12*w//125+50,4*h//10+100+50), func=self.__select_wall4, cam=1)
        self.camera_height_lbl_1 = Label(offset_x+2*12*w//125, 4*h//10+50, 100, 30, text="Y (mm):")
        self.camera_height_inp_1 = InputBox(offset_x+2*12*w//125, 4*h//10+100, 100, 50, func=self.__set_camera_height, cam=1)
        self.camera_width_lbl_1 = Label(offset_x+3*12*w//125, 4*h//10+50, 100, 30, text="X (mm):")
        self.camera_width_inp_1 = InputBox(offset_x+3*12*w//125, 4*h//10+100, 100, 50, func=self.__set_camera_width, cam=1)
        self.secondary_lbl = Label(offset_x, 7*h//10, 100, 50, text="Secondary Camera:")
        self.name_lbl_2 = Label(offset_x, 7*h//10+50, 100, 30, text="name:")
        self.name_inp_2 = InputBox(offset_x, 7*h//10+100, 100, 50,func=self.__set_camera_name, cam=2)
        self.wall_lbl_2 = Label(offset_x+12*w//125, 7*h//10+50, 100, 30, text="select wall:")
        wall_icon = np.full((30,30,4), (255,255,0,50), np.uint8)
        wall_selected_icon[5:26,5:26] = (255,255,0,200)
        self.wall1_btn_2 = ImageButton(wall_icon, wall_selected_icon, 30,30,(offset_x+12*w//125,7*h//10+100),func=self.__select_wall1, cam=2)
        wall_icon = np.full((30,30,4), (0,255,0,50), np.uint8)
        wall_selected_icon[5:26,5:26] = (0,255,0,200)
        self.wall2_btn_2 = ImageButton(wall_icon, wall_selected_icon, 30,30,(offset_x+12*w//125+50,7*h//10+100),func=self.__select_wall2, cam=2)
        wall_icon = np.full((30,30,4), (0,0,255,50), np.uint8)
        wall_selected_icon[5:26,5:26] = (0,0,255,200)
        self.wall3_btn_2 = ImageButton(wall_icon, wall_selected_icon, 30,30,(offset_x+12*w//125,7*h//10+100+50),func=self.__select_wall3,  cam=2)
        wall_icon = np.full((30,30,4), (255,0,0,50), np.uint8)
        wall_selected_icon[5:26,5:26] = (255,0,0,200)
        self.wall4_btn_2 = ImageButton(wall_icon, wall_selected_icon, 30,30,(offset_x+12*w//125+50,7*h//10+100+50),func=self.__select_wall4,  cam=2)
        self.camera_height_lbl_2 = Label(offset_x+2*12*w//125, 7*h//10+50, 100, 30, text="Y (mm):")
        self.camera_height_inp_2 = InputBox(offset_x+2*12*w//125, 7*h//10+100, 100, 50, func=self.__set_camera_height, cam=2)
        self.camera_width_lbl_2 = Label(offset_x+3*12*w//125, 7*h//10+50, 100, 30, text="X (mm):")
        self.camera_width_inp_2 = InputBox(offset_x+3*12*w//125, 7*h//10+100, 100, 50, func=self.__set_camera_width, cam=2)
        self.primary_browse_lbl = Label(offset_x+4*12*w//125, 4*h//10+50, 100, 50, text="Camera Parameters")
        self.primary_browse_btn = Button("Browse", 100, 50, (offset_x+4*12*w//125, 4*h//10+100), func=self.__get_primary_projection_matrix)
        self.secondary_browse_lbl = Label(offset_x+4*12*w//125, 7*h//10+50, 100, 50, text="Camera Parameters")
        self.secondary_browse_btn = Button("Browse", 100, 50, (offset_x+4*12*w//125, 7*h//10+100), func=self.__get_secondary_projection_matrix)

        self.next_step_btn = Button("Next Step", 300, 50, (screen.get_width()-400,screen.get_height()-150), func=self.__next_step)

        self.video1_btn = Button("Load calibration video 1", w/4, 50, (w//8, 50), func=self.__load_video1)
        self.video2_btn = Button("Load calibration video 2", w/4, 50, (screen.get_width()-w//8-w/4, 50), func=self.__load_video2)
        self.next_frame_btn = Button("next frame", 300, 50, (screen.get_width()-750, screen.get_height()-150), func=self.__next_frame)
        self.select_btn = Button("select frame", 300, 50, (screen.get_width()-400, screen.get_height()-150), func=self.__next_step)
        
        self.img1_lbl = Label((screen.get_width()-400)//3, 0, 200, 50)
        self.img2_lbl = Label(screen.get_width()-(screen.get_width()-400)//3-200, 0, 200, 50)
        self.pos_w_lbl = Label(screen.get_width()//3,2*screen.get_height()//3+50, 2*screen.get_height()//9, 50, text="X")
        self.pos_w_inp = InputBox(screen.get_width()//3,2*screen.get_height()//3+100, 100, 50, text="w", func=self.__set_pos_w)
        self.pos_h_lbl = Label(screen.get_width()//3+150,2*screen.get_height()//3+50, 100, 50, text="Y")
        self.pos_h_inp = InputBox(screen.get_width()//3+150,2*screen.get_height()//3+100, 100, 50, text="h", func=self.__set_pos_h)
        self.pos_d_lbl = Label(screen.get_width()//3+2*150,2*screen.get_height()//3+50, 100, 50, text="Z")
        self.pos_d_inp = InputBox(screen.get_width()//3+2*150,2*screen.get_height()//3+100, 100, 50, text="d", func=self.__set_pos_d)
        self.get_point_lbl = Label(screen.get_width()//3, 2*screen.get_height()//3, 200, 300)
        self.next_btn = Button("NEXT", 100,50, (2*screen.get_width()//3, 2*screen.get_height()//3+100), func=self.__next)
        self.reset_btn = Button("RESET", 100,50, (2*screen.get_width()//3+150, 2*screen.get_height()//3+100), func=self.__reset_positions)

        self.restart_btn = Button("restart", 300, 50, (screen.get_width()-750, screen.get_height()-150), func=self.__restart)
        self.done_btn = Button("done", 300, 50, (screen.get_width()-400,screen.get_height()-150),func=self.__done)

        self.__init()

        self.browse_2d_kp_btn = Button("add 2d keypoint file", w/3, 50, (w//12, 200), func=self.__add_kp_file)
        self.kp_files_list_lbl = Label(w//12, 350, w/3, h/2)
        self.kp_files_list = []
        self.add_calibration_btn = Button("add calibration parameteres", w/3, 50, (7*w//12, 200), func=self.__add_calibration_file)
        self.calibraion_list_lbl = Label(7*w//12, 350, w/3, h/2)
        self.reconstruction_files = []
        self.vis_3d_btn = Button("Visualize 3D", 300, 50, (screen.get_width()-200,screen.get_height()-200), func=self.__convert_2d_3d)


    def __open_jarvis(self):
        os.system("AnnotationTool")

    def __init(self):
        self.project_name = ''
        self.project_name_inp.text = self.project_name
        self.name_inp_1.text = ''
        self.camera_height_inp_1.text = ''
        self.camera_width_inp_1.text = ''
        self.name_inp_2.text = ''
        self.camera_height_inp_2.text = ''
        self.camera_width_inp_2.text = ''
        self.camera_config_list = {1:{}, 2:{}}
        self.camera_pos = dict()
        self.selected_wall = 0
        self.frame1 = None
        self.frame2 = None
        self.positions1 = []
        self.positions2 = []
        self.real_pos = []
        self.pos_i = 0

    def __set_project_name(self):
        self.project_name = self.project_name_inp.text

    def __render_cube(self):
        w = self.cube_width
        h = self.cube_height
        d = self.cube_depth
        # cube = [[0,-h,d],[w,-h,d],[w,0,d],[0,0,d],[0,-h,0],[w,-h,0],[w,0,0],[0,0,0]]
        # cube = [[0,0,0],(w,0,0),[w,h,0],[0,h,0],[0,0,d],[w,0,d],[w,h,d],[0,h,d]]
        cube = [[-w/2,-h/2,d/2],[w/2,-h/2,d/2],[w/2,h/2,d/2],[-w/2,h/2,d/2],[-w/2,-h/2,-d/2],[w/2,-h/2,-d/2],[w/2,h/2,-d/2],[-w/2,h/2,-d/2]]
        cube.extend([[cube[6][0]+1000, cube[6][1], cube[6][2]], [cube[6][0], cube[6][1]+1000, cube[6][2]], [cube[6][0], cube[6][1], cube[6][2]+1000]])
        projection_matrix = [[1,0],[0,1],[0,0]]

        rotation_matrix = rotation_x(self.tetha_x)
        rotation_matrix = np.dot(rotation_matrix, rotation_y(self.tetha_y))
        rotation_matrix = np.dot(rotation_matrix, rotation_z(self.tetha_z))
        rotated_cube = np.dot(cube, rotation_matrix)
        projected_2d = np.dot(rotated_cube, projection_matrix)

        return projected_2d, rotation_matrix

    def __change_width(self):
        self.cube_width = int(re.search(r'\d+', self.width_inp.text).group())

    def __change_height(self):
        self.cube_height = int(re.search(r'\d+', self.height_inp.text).group())

    def __change_depth(self):
        self.cube_depth = int(re.search(r'\d+', self.depth_inp.text).group())

    def __set_camera_name(self, cam):
        self.camera_config_list[cam]["name"] = getattr(self,f"name_inp_{cam}").text

    def __select_wall1(self, cam):
        for i in range(1,5):
            getattr(self,f"wall{i}_btn_{cam}").isClicked = False
        self.selected_wall=1
        self.tetha_y = -30
        self.tetha_x = -20
        self.camera_pos[cam] = (0, 0, -self.cube_depth//2)
        self.camera_config_list[cam]["wall"] = 1

    def __select_wall2(self, cam):
        for i in range(1,5):
            getattr(self,f"wall{i}_btn_{cam}").isClicked = False
        self.selected_wall=2
        self.tetha_y = - 60
        self.tetha_x = -20
        self.camera_pos[cam] = (self.cube_width//2, 0, 0)
        self.camera_config_list[cam]["wall"] = 2

    def __select_wall3(self, cam):
        for i in range(1,5):
            getattr(self,f"wall{i}_btn_{cam}").isClicked = False
        self.selected_wall=3
        self.tetha_y = 90+ 60
        self.tetha_x = 20
        self.camera_pos[cam] = (-self.cube_width//2, 0, 0)
        self.camera_config_list[cam]["wall"] = 3

    def __select_wall4(self, cam):
        for i in range(1,5):
            getattr(self,f"wall{i}_btn_{cam}").isClicked = False
        self.selected_wall=4
        self.tetha_y = 180 - 30
        self.tetha_x = 20
        self.camera_pos[cam] = (0, 0, self.cube_depth//2)
        self.camera_config_list[cam]["wall"] = 4

    def __set_camera_width(self, cam):
        camera_width = int(re.search(r'\d+',  getattr(self,f"camera_width_inp_{cam}").text).group())
        if self.selected_wall ==1 :
            self.camera_pos[cam] = (camera_width-(self.cube_width//2), self.camera_pos[cam][1], self.camera_pos[cam][2])
        elif self.selected_wall==2:
            self.camera_pos[cam] = (self.camera_pos[cam][0], self.camera_pos[cam][1], camera_width-(self.cube_depth//2))
        elif self.selected_wall==3:
            self.camera_pos[cam] = (self.camera_pos[cam][0], self.camera_pos[cam][1], (self.cube_depth//2)-camera_width)
        elif self.selected_wall==4:
            self.camera_pos[cam] = ((self.cube_width//2)-camera_width, self.camera_pos[cam][1], self.camera_pos[cam][2])
        
    def __set_camera_height(self, cam):
        camera_height = int(re.search(r'\d+',  getattr(self,f"camera_height_inp_{cam}").text).group())
        self.camera_pos[cam] = (self.camera_pos[cam][0], (self.cube_height//2) - camera_height, self.camera_pos[cam][2])

    def __add_camera(self):
        for c in [1, 2]:
            position = None
            if self.selected_wall==1:
                flip = (-1,-1,1)
                position = (self.camera_pos[c][0]-self.cube_width//2, self.camera_pos[c][1]-self.cube_height//2, 0)
            elif self.selected_wall==2:
                flip = (-1,-1,-1)
                position = (0, self.camera_pos[c][1]-self.cube_height//2, self.cube_depth//2+self.camera_pos[c][2])    
            elif self.selected_wall==3:
                flip = (1,-1,1)
                position = (-self.cube_width, self.camera_pos[c][1]-self.cube_height//2, self.cube_depth//2+self.camera_pos[c][0])
            
            elif self.selected_wall==4:
                # flip = (1, -1, -1)
                flip = (-1,-1,1)
                position = (self.camera_pos[c][0] - self.cube_width//2, self.camera_pos[c][1]-self.cube_height//2, self.cube_depth//2+self.camera_pos[c][2])
            self.camera_config_list[c]["pos"] = self.camera_pos[c]
            self.camera_config_list[c]["world_pos"]=position
            self.camera_config_list[c]['flip']= flip
        
    def __next_step(self):
        if self.step == 1:
            self.__add_camera()
        self.step += 1

    def __convert_2d_3d(self):
        classes = ['Vin', 'Nathan'] # monkeys
        conf_thresh = 0.1
        num_frames = 19635 # fps * seconds

        self.key_points_3d = []
        for files in self.reconstruction_files:
            with open(files[0][0]) as file:
                input_stream1_lines = [line.rstrip() for line in file]
            with open(files[0][1]) as file:
                input_stream2_lines = [line.rstrip() for line in file]
            input_stream1_lines.pop(0)
            input_stream2_lines.pop(0)
            for i in range(len(input_stream1_lines)):
                input_stream1_lines[i] = input_stream1_lines[i].split(' ')
            for i in range(len(input_stream2_lines)):
                input_stream2_lines[i] = input_stream2_lines[i].split(' ')

            with open(files[1], 'rb') as f:
                calibration_data = pickle.load(f)

            kpts_3d = run_3d(input_stream1_lines, input_stream2_lines, calibration_data["primary_mat"], calibration_data["secondary_mat"], calibration_data["transformation_mat"], [np.abs(x) for x in calibration_data["primary_cam"]['world_pos']], calibration_data["primary_cam"]['flip'], classes, num_frames, conf_thresh)
            self.key_points_3d.append(kpts_3d)

        self.frame_generator = combine(self.key_points_3d, monkeys=['Vin', 'Nathan'])
        self.step+=1


    def __prompt_file(self):
        """Create a Tk file dialog and cleanup when finished"""
        top = tkinter.Tk()
        top.withdraw()  # hide window
        file_name = tkinter.filedialog.askopenfilename(parent=top)
        top.destroy()
        print(file_name)
        return file_name
    
    def __get_primary_projection_matrix(self):
        file = self.__prompt_file()
        P = get_projection_matrix(file)
        self.primary_P_mat = P

    def __get_secondary_projection_matrix(self):
        file = self.__prompt_file()
        P = get_projection_matrix(file)
        self.secondary_P_mat = P
    
    def __load_video1(self):
        file = self.__prompt_file()
        self.cap1 = cv2.VideoCapture(file)
        _, self.frame1 = self.cap1.read()

    def __load_video2(self):
        file = self.__prompt_file()
        self.cap2 = cv2.VideoCapture(file)
        _, self.frame2 = self.cap2.read()

    def __next_frame(self):
        _, self.frame1 = self.cap1.read()
        _, self.frame2 = self.cap2.read()

    def __set_pos_w(self):
        self.pos_w = int(re.search(r'\d+', self.pos_w_inp.text).group())
        self.pos_w = self.pos_w - self.camera_config_list[1]['world_pos'][0]
    
    def __set_pos_h(self):
        self.pos_h = int(re.search(r'\d+', self.pos_h_inp.text).group())
        self.pos_h = self.pos_h - self.camera_config_list[1]['world_pos'][1]

    def __set_pos_d(self):
        self.pos_d = int(re.search(r'\d+', self.pos_d_inp.text).group())
        self.pos_d = self.pos_d - self.camera_config_list[1]['world_pos'][2]

    def __next(self):
        self.pos_i += 1
        self.real_pos.append((self.pos_w, self.pos_h, self.pos_d))
    
    def __reset_positions(self):
        self.positions1 = []
        self.positions2 = []
        self.real_pos = []
        self.pos_i = 0

    def __done(self):
        self.__process()
        self.__init()
        self.step = 0

    def __restart(self):
        self.__process()
        self.__init()
        self.step=1

    def __process(self):
        self.real_pos.append((self.pos_w, self.pos_h, self.pos_d))

        transformation_matrix = find_transformation_matrix(self.primary_P_mat, self.secondary_P_mat, self.positions1, self.positions2, self.real_pos)
                        
        data = {
            "primary_mat": self.primary_P_mat,
            "secondary_mat": self.secondary_P_mat,
            "transformation_mat": transformation_matrix,
            "primary_cam": self.camera_config_list[1]
        }
        with open(f"{self.project_name}.pickle", 'wb') as f:
            pickle.dump(data, f)


    def __add_kp_file(self):
        file = self.__prompt_file()
        self.kp_files_list.append(file)
        self.kp_files_list_lbl.text = '\n'.join(self.kp_files_list)

    def __add_calibration_file(self):
        file = self.__prompt_file()
        self.reconstruction_files.append((self.kp_files_list[-2:], file))
        self.calibraion_list_lbl.text = '\n'.join([a[1] for a in self.reconstruction_files])

    def __select_option(self, option):
        self.step = option

    def run(self):
        done = False


        rotation_matrix = rotation_x(120)
        rotation_matrix = np.dot(rotation_matrix, rotation_y(30))
        rotation_matrix = np.dot(rotation_matrix, rotation_z(30))

        scale = 1
        position = (1000,3000)
        cube = [[0,2400,0],[0,2400,4500],[2700,2400,4500],[2700,2400,0],[0,0,0],[0,0,4500],[2700,0,4500],[2700,0,0]]
        cube = np.dot(cube, rotation_matrix)
        projection_matrix = [[1,0],[0,1],[0,0]]

        classes = ['Vin', 'Nathan']  # nathan vin

        while not done:
            ## get and handle events in this frame
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == QUIT:
                    # cap.release()
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        # cap.release()
                        pygame.quit()
                        sys.exit()

            screen.fill((255, 255, 255))

            if self.step == 0: ## menu
                self.menu_jarvis_btn.draw(screen)
                self.menu_calibration_btn.draw(screen)
                self.menu_visualization_btn.draw(screen)

            if self.step==1 or self.step==2:
                scale = 0.1
                position = (300,500)
                canvas = np.ones((screen.get_height(),700,4), np.uint8)*250
                projected_2d, mat_r = self.__render_cube()
                projected_2d = np.int32(position+scale*projected_2d)
                for point in projected_2d[:8]:
                    cv2.circle(canvas, point, 3, (0,0,0,255), -1)
                
                for i in range(4):
                    cv2.line(canvas, projected_2d[i], projected_2d[(i+1)%4], (0,0,0,255), 2)
                    cv2.line(canvas, projected_2d[4+i], projected_2d[4+(i+1)%4], (0,0,0,255), 2)
                    cv2.line(canvas, projected_2d[i], projected_2d[i+4], (0,0,0,255), 2)

                # ### roof
                # roof_points = np.array([projected_2d[i]-(0,200) for i in [0,1,5,4]], np.int32)
                # for i, point in enumerate(roof_points):
                #     cv2.circle(canvas, point, 3, (0,0,0,255), -1)
                # cv2.fillPoly(canvas, [roof_points], (255,0,255,50))
                    
                if self.selected_wall > 0:
                    if self.selected_wall==1:
                        cv2.fillPoly(canvas, [projected_2d[:4]], (255,0,0,50))
                        cv2.fillPoly(canvas, [np.array([projected_2d[0],projected_2d[3],projected_2d[7],projected_2d[4]])], (0,0,255,50))
                        cv2.fillPoly(canvas, [np.array([projected_2d[1],projected_2d[2],projected_2d[6],projected_2d[5]])], (0,255,0,50))
                        cv2.fillPoly(canvas, [projected_2d[4:8]], (255,255,0,200))
                        cv2.line(canvas, projected_2d[4], projected_2d[7], (0,0,0,255), 5)
                        cv2.line(canvas, projected_2d[6], projected_2d[7], (0,0,0,255), 5)
                    elif self.selected_wall==2:
                        cv2.fillPoly(canvas, [np.array([projected_2d[0],projected_2d[3],projected_2d[7],projected_2d[4]])], (0,0,255,50))
                        cv2.fillPoly(canvas, [projected_2d[4:8]], (255,255,0,50))
                        cv2.fillPoly(canvas, [projected_2d[:4]], (255,0,0,50))
                        cv2.fillPoly(canvas, [np.array([projected_2d[1],projected_2d[2],projected_2d[6],projected_2d[5]])], (0,255,0,200))
                        cv2.line(canvas, projected_2d[5], projected_2d[6], (0,0,0,255), 5)
                        cv2.line(canvas, projected_2d[6], projected_2d[2], (0,0,0,255), 5)
                    elif self.selected_wall==3:
                        cv2.fillPoly(canvas, [np.array([projected_2d[1],projected_2d[2],projected_2d[6],projected_2d[5]])], (0,255,0,50))
                        cv2.fillPoly(canvas, [projected_2d[:4]], (255,0,0,50))
                        cv2.fillPoly(canvas, [projected_2d[4:8]], (255,255,0,50))
                        cv2.fillPoly(canvas, [np.array([projected_2d[0],projected_2d[3],projected_2d[7],projected_2d[4]])], (0,0,255,200))
                        cv2.line(canvas, projected_2d[0], projected_2d[3], (0,0,0,255), 5)
                        cv2.line(canvas, projected_2d[3], projected_2d[7], (0,0,0,255), 5)
                    elif self.selected_wall==4:
                        cv2.fillPoly(canvas, [projected_2d[4:8]], (255,255,0,50))
                        cv2.fillPoly(canvas, [np.array([projected_2d[1],projected_2d[2],projected_2d[6],projected_2d[5]])], (0,255,0,50))
                        cv2.fillPoly(canvas, [np.array([projected_2d[0],projected_2d[3],projected_2d[7],projected_2d[4]])], (0,0,255,50))
                        cv2.fillPoly(canvas, [projected_2d[:4]], (255,0,0,200))
                        cv2.line(canvas, projected_2d[1], projected_2d[2], (0,0,0,255), 5)
                        cv2.line(canvas, projected_2d[2], projected_2d[3], (0,0,0,255), 5)


                    for k, v in self.camera_config_list.items():
                        if k in self.camera_pos.keys():
                            # pos = np.dot(v['pos'], mat_r)[:2]
                            pos = np.dot(self.camera_pos[k], mat_r)[:2]
                            pos = np.int32(position+scale*pos)
                            cv2.circle(canvas, pos, 10, (50,50,50,150), )    
                    # pos = np.dot(self.camera_pos, mat_r)[:2]
                    # pos = np.int32(position+scale*pos)
                    # cv2.circle(canvas, pos, 10, (0,0,0,255), 5)
                else:
                    cv2.fillPoly(canvas, [projected_2d[:4]], (255,0,0,50))
                    cv2.fillPoly(canvas, [np.array([projected_2d[0],projected_2d[3],projected_2d[7],projected_2d[4]])], (0,0,255,50))
                    cv2.fillPoly(canvas, [np.array([projected_2d[1],projected_2d[2],projected_2d[6],projected_2d[5]])], (0,255,0,50))
                    cv2.fillPoly(canvas, [projected_2d[4:8]], (255,255,0,50))

                x_ = np.min([x[0] for x in projected_2d[:8]]) - 5
                w_ = np.max([x[0] for x in projected_2d[:8]]) - x_ +10
                y_ = np.min([x[1] for x in projected_2d[:8]])-5
                h_ = np.max([x[1] for x in projected_2d[:8]]) - y_+10
                if (w_ > h_):
                    canvas = canvas[y_ - (w_-h_)//2:y_+h_+(w_-h_)//2, x_:x_+w_]
                else:
                    canvas = canvas[y_:y_+h_, x_ - (h_-w_)//2: x_+w_+(h_-w_)//2]
                canvas = cv2.resize(canvas, (int(3*screen.get_width()//10), int(3*screen.get_width()//10)))

                screen.blit(pygame.image.frombuffer(canvas.tobytes(), (canvas.shape[1],canvas.shape[0]), "RGBA"), (screen.get_width()-canvas.shape[1]-50,100))

                self.project_name_lbl.draw(screen)
                self.project_name_inp.draw(screen, self.events)

                self.width_lbl.draw(screen)
                self.width_inp.draw(screen, self.events)
                self.height_lbl.draw(screen)
                self.height_inp.draw(screen, self.events)
                self.depth_lbl.draw(screen)
                self.depth_inp.draw(screen, self.events)

                self.primary_lbl.draw(screen)
                self.name_lbl_1.draw(screen)
                self.name_inp_1.draw(screen, self.events)
                self.wall_lbl_1.draw(screen)
                self.wall1_btn_1.draw(screen)
                self.wall2_btn_1.draw(screen)
                self.wall3_btn_1.draw(screen)
                self.wall4_btn_1.draw(screen)
                self.camera_height_lbl_1.draw(screen)
                self.camera_height_inp_1.draw(screen, self.events)
                self.camera_width_lbl_1.draw(screen)
                self.camera_width_inp_1.draw(screen, self.events)
                self.secondary_lbl.draw(screen)
                self.name_lbl_2.draw(screen)
                self.name_inp_2.draw(screen, self.events)
                self.wall_lbl_2.draw(screen)
                self.wall1_btn_2.draw(screen)
                self.wall2_btn_2.draw(screen)
                self.wall3_btn_2.draw(screen)
                self.wall4_btn_2.draw(screen)
                self.camera_height_lbl_2.draw(screen)
                self.camera_height_inp_2.draw(screen, self.events)
                self.camera_width_lbl_2.draw(screen)
                self.camera_width_inp_2.draw(screen, self.events)

                if self.step==2:
                    self.primary_browse_lbl.draw(screen)
                    self.primary_browse_btn.draw(screen)
                    self.secondary_browse_lbl.draw(screen)
                    self.secondary_browse_btn.draw(screen)

                self.next_step_btn.draw(screen)
                    

            elif self.step==3:
                self.video1_btn.draw(screen)
                self.video2_btn.draw(screen)
                
                if self.frame1 is not None:
                    r = self.frame1.shape[1]/self.frame1.shape[0]
                    w = 4*screen.get_width()//10
                    h = w/r
                    x = screen.get_width()/20
                    img1 = cv2.resize(self.frame1, (int(w),int(h)))
                    screen.blit(pygame.image.frombuffer(img1.tobytes(), (img1.shape[1],img1.shape[0]), "RGB"), (x,150))
                if self.frame2 is not None:
                    r = self.frame2.shape[1]/self.frame2.shape[0]
                    w = 4*screen.get_width()//10
                    h = w/r
                    x = screen.get_width()/20
                    img2 = cv2.resize(self.frame2, (int(w),int(h)))
                    screen.blit(pygame.image.frombuffer(img2.tobytes(), (img2.shape[1],img2.shape[0]), "RGB"), (screen.get_width()-int(w)-x,150))

                self.next_frame_btn.draw(screen)
                self.select_btn.draw(screen)

            elif self.step==4:
                img1_ = self.frame1.copy()
                img2_ = self.frame2.copy()
                for pos1 in self.positions1[:self.pos_i]:
                    cv2.circle(img1_, np.uint16(pos1), 10, (0,255,0), -1)
                if len(self.positions1)==self.pos_i+1: cv2.circle(img1_, np.uint16(self.positions1[self.pos_i]), 10, (255,0,0), -1)
                for pos2 in self.positions2[:self.pos_i]:
                    cv2.circle(img2_, np.uint16(pos2), 10, (0,255,0), -1)
                if len(self.positions2)==self.pos_i+1: cv2.circle(img2_, np.uint16(self.positions2[self.pos_i]), 10, (255,0,0), -1)
                r = img1_.shape[0]/img1_.shape[1]
                w = 2*screen.get_width()//5
                h = w*r

                img1_rect = pygame.Rect(int(w/6),50,img1_.shape[1], img1_.shape[0])
                img2_rect = pygame.Rect(screen.get_width()-w-int(w/6),50,img2_.shape[1], img2_.shape[0])
                if len(self.positions1) == self.pos_i:
                    mouse_pos = pygame.mouse.get_pos()
                    if img1_rect.collidepoint(mouse_pos):
                        if pygame.mouse.get_pressed()[0]:
                            self.positions1.append(((mouse_pos[0] - img1_rect.x)*img1_.shape[1]/w, (mouse_pos[1]-img1_rect.y)*img1_.shape[0]/h))
                if len(self.positions2) == self.pos_i:
                    mouse_pos = pygame.mouse.get_pos()
                    if img2_rect.collidepoint(mouse_pos):
                        if pygame.mouse.get_pressed()[0]:
                            self.positions2.append(((mouse_pos[0] - img2_rect.x)*img2_.shape[1]/w, (mouse_pos[1]-img2_rect.y)*img2_.shape[0]/h))

                img1_ = cv2.resize(img1_, (int(w), int(h)))
                img2_ = cv2.resize(img2_, (int(w), int(h)))
                self.img1_lbl.text = f"View of Camera {self.camera_config_list[1]['name']}"
                self.img2_lbl.text = f"View of Camera {self.camera_config_list[2]['name']}"
                self.img1_lbl.draw(screen)
                self.img2_lbl.draw(screen)
                screen.blit(pygame.image.frombuffer(img1_.tobytes(), (img1_.shape[1],img1_.shape[0]), "RGB"), (int(w/6),50))
                screen.blit(pygame.image.frombuffer(img2_.tobytes(), (img2_.shape[1],img2_.shape[0]), "RGB"), (screen.get_width()-w-int(w/6),50))


                if self.pos_i==3:
                    self.restart_btn.draw(screen)
                    self.done_btn.draw(screen)
                elif len(self.positions1)==self.pos_i+1 and len(self.positions2)==self.pos_i+1:
                    self.get_point_lbl.text = f"enter world coordinate for point {self.pos_i+1} out of 3:"
                    # self.get_point_lbl.y = h + 100
                    self.get_point_lbl.draw(screen)
                    self.pos_w_lbl.draw(screen)
                    self.pos_w_inp.draw(screen,self.events)
                    self.pos_h_lbl.draw(screen)
                    self.pos_h_inp.draw(screen,self.events)
                    self.pos_d_lbl.draw(screen)
                    self.pos_d_inp.draw(screen,self.events)

                    scale = 0.05
                    position = (130,100)
                    canvas = np.ones((300,300,4), np.uint8)*250
                    if self.camera_config_list[1]["wall"] == 1:
                        self.tetha_y = -30
                        self.tetha_x = -20
                    elif self.camera_config_list[1]["wall"] == 2:
                        self.tetha_y = - 60
                        self.tetha_x = -20
                    elif self.camera_config_list[1]["wall"] == 3:
                        self.tetha_y = 90+ 60
                        self.tetha_x = 20
                    elif self.camera_config_list[1]["wall"] == 4:
                        self.tetha_y = 180 - 30
                        self.tetha_x = 20
                    projected_2d, mat_r = self.__render_cube()
                    projected_2d = np.int32(position+scale*projected_2d)
                    for point in projected_2d[:8]:
                        cv2.circle(canvas, point, 3, (0,0,0,255), -1)
                    
                    for i in range(4):
                        cv2.line(canvas, projected_2d[i], projected_2d[(i+1)%4], (0,0,0,255), 2)
                        cv2.line(canvas, projected_2d[4+i], projected_2d[4+(i+1)%4], (0,0,0,255), 2)
                        cv2.line(canvas, projected_2d[i], projected_2d[i+4], (0,0,0,255), 2)
                    

                    if self.camera_config_list[1]["wall"] == 1:
                        cv2.fillPoly(canvas, [projected_2d[4:8]], (0,255,255,150))
                    elif self.camera_config_list[1]["wall"] == 2:
                        cv2.fillPoly(canvas, [np.array([projected_2d[1],projected_2d[2],projected_2d[6],projected_2d[5]])], (0,255,255,150))
                    elif self.camera_config_list[1]["wall"] == 3:
                        cv2.fillPoly(canvas, [np.array([projected_2d[0],projected_2d[3],projected_2d[7],projected_2d[4]])], (0,255,255,150))
                    elif self.camera_config_list[1]["wall"] == 4:
                        cv2.fillPoly(canvas, [projected_2d[:4]], (0,255,255,150))
                    cv2.circle(canvas, projected_2d[6], 5, (255,0,0,255))

                    cv2.line(canvas, projected_2d[6], projected_2d[8], (255,0,0,255), 3)
                    cv2.line(canvas, projected_2d[6], projected_2d[9], (0,255,0,255), 3)
                    cv2.line(canvas, projected_2d[6], projected_2d[10], (0,0,255,255), 3)

                    x_ = np.min([x[0] for x in projected_2d]) - 5
                    w_ = np.max([x[0] for x in projected_2d]) - x_ +10
                    y_ = np.min([x[1] for x in projected_2d])-5
                    h_ = np.max([x[1] for x in projected_2d]) - y_+10
                    if (w_ > h_):
                        canvas = canvas[y_ - (w_-h_)//2:y_+h_+(w_-h_)//2, x_:x_+w_]
                    else:
                        canvas = canvas[y_:y_+h_, x_ - (h_-w_)//2: x_+w_+(h_-w_)//2]
                    canvas = cv2.resize(canvas, (int(w/3), int(w/3)))

                    screen.blit(pygame.image.frombuffer(canvas.tobytes(), (canvas.shape[1],canvas.shape[0]), "RGBA"), ((screen.get_width()//3-w//3)//2,(h+100)+(screen.get_height()-h-100-w//3)//2))
                        
                    self.next_btn.draw(screen)
                    self.reset_btn.draw(screen)

            if self.step == 11:
                self.browse_2d_kp_btn.clickable = True
                self.add_calibration_btn.clickable = False
                if len(self.kp_files_list) > 0 and len(self.kp_files_list)%2==0:
                    self.browse_2d_kp_btn.clickable = False
                    self.add_calibration_btn.clickable = True
                if len(self.reconstruction_files) == len(self.kp_files_list)/2:
                    self.browse_2d_kp_btn.clickable = True
                    self.add_calibration_btn.clickable = False
                self.browse_2d_kp_btn.draw(screen)
                self.kp_files_list_lbl.draw(screen)
                self.add_calibration_btn.draw(screen)
                self.calibraion_list_lbl.draw(screen)

                self.vis_3d_btn.draw(screen)

            elif self.step == 12:
                canvas = np.ones((6000,7000,3), np.uint8)*255
                # list_of_monkeys = [self.input_3d1_lines.pop(0), self.input_3d2_lines.pop(0)]
                list_of_monkeys = next(self.frame_generator)

                projected_2d = np.dot(cube, projection_matrix)
                projected_2d = np.int32(position+scale*projected_2d)
                for point in projected_2d:
                    cv2.circle(canvas, point, 5, (200,200,200), -1)
                
                for j in range(4):
                    cv2.line(canvas, projected_2d[j], projected_2d[(j+1)%4], (200,200,200), 5)
                    cv2.line(canvas, projected_2d[4+j], projected_2d[4+(j+1)%4], (200,200,200), 5)
                    cv2.line(canvas, projected_2d[j], projected_2d[j+4], (200,200,200), 5)


                for idx, mnky in enumerate(['Vin', 'Nathan']):
                    p3ds = list_of_monkeys[mnky]
                    p3ds = np.array(p3ds).reshape((17, 3))
                    projected_points = []
                    for point in p3ds:
                        if point[0] != -1:
                            pos = np.dot(point, rotation_matrix)[:2]
                            pos = np.int32(position+scale*pos)
                            projected_points.append(pos)
                            cv2.circle(canvas, pos, 7, colors[idx], -1)    
                        else:
                            projected_points.append([0,0])
                    for _c in connections:
                        if p3ds[_c[0], 0] != -1 and p3ds[_c[1], 0] != -1:
                            cv2.line(canvas, projected_points[_c[0]], projected_points[_c[1]], colors[idx], 5)
                
                r = canvas.shape[1] / canvas.shape[0]
                h = screen.get_height()
                w = r * h
                canvas = cv2.resize(canvas, (int(w),int(h)))
                screen.blit(pygame.image.frombuffer(canvas.tobytes(), (canvas.shape[1],canvas.shape[0]), "RGB"), (screen.get_width()-canvas.shape[1],0))


            ### update the screen and limit max framerate
            pygame.display.update()
            mainClock.tick(60)
    

if __name__ == "__main__":
    
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption('Calibration')
    screen = pygame.display.set_mode((0, 0)) # , pygame.FULLSCREEN
    print(screen.get_height(), screen.get_width())
    mainClock = pygame.time.Clock()

    app = App()
    app.run()
