'''

Culture Chef

Creates Gif sets from old archive films

Chef makes them - server serves.

@alexparsons

'''
from internetarchive import search_items, get_item, download
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from funcs.ql import QuickList
import os
import random
import subprocess
import shutil

def move_good_clips():
    ql = QuickList().open("F:\\mp4s\\joined.xls")
    
    folder = "F:\\mp4s"
    dest = "F:\\mp4s\\good"
    for r in ql:
        shutil.move(os.path.join(folder,r["file_name"]),os.path.join(dest,r["file_name"]))
    

def create_preview_from_schedule():
    """
    generates preview of all videos to review
    """
    ql = QuickList().open("F:\\mp4s\\joined.xls")
    
    template = '''<h1>{0}</h1>
                        <h2>{1}</h2>
                    <video width="320" height="240" loop autoplay>
                      <source src="{2}" type="video/mp4">
                    Your browser does not support the video tag.
                    </video>
                                    '''
    
    entries = []
    count = 0
    
    for x,r in enumerate(ql):
        entries.append(template.format(r['file_name'],
                                       r['nice_title'],
                                       os.path.join("../",r['file_name'])
                                       ))
        if x and x % 5 == 0 or x == len(ql.data) - 1:
            text = "".join(entries)
            text += '<h2><a href="{0}.html">Next</a></h2>'.format(count+1)
            with open("F:\\mp4s\\review\\{0}.html".format(count),"wb") as f:
                f.write(text)
            entries = []
            count += 1
    
    


def make_small_gif(gif_path="F:\\input_gif.gif"):
    """
    shrink gif
    """
    output_file = 'F:\\\output.gif'
    video = VideoFileClip(gif_path).resize(0.6)
    length = int(video.fps * video.duration)
    
    video.write_gif(output_file,
                   fps=video.fps,
                   program="ffmpeg")
    

    new_frame_speed = int(1/(video.fps/2) * 100)
          
    options = ["gifsicle",
               output_file,
               '-O3',
               '-o', output_file
               
               ]
    result = subprocess.Popen(options,
                              stdout = subprocess.PIPE,
                              stderr = subprocess.STDOUT)
    for l in result.stdout.readlines():
        print l    


def make_clip(path,out_dir,framerate,start,end):
    """
    create gifs - given path and timecode-
    """
    video = VideoFileClip(path)
    print "loaded"
    clip = video.subclip(start,end).without_audio()
    frame = clip.get_frame(1)

    """get average luma"""
    lumas = []
    for l in frame:
        for f in l:
            r,g,b = f
            luma =  0.2126*r + 0.7152*g + 0.0722*b
            lumas.append(luma)
            
    average_luma = round(sum(lumas)/float(len(lumas)),2)
    
    if average_luma < 40: #gets rid of dark scenes (bad scenes)
        return 0

    mp4_file = os.path.join(out_dir,'clip_{0}.mp4'.format(start))
    gif_file = os.path.join(out_dir,'clip_{0}.gif'.format(start))
    
    score = 0
    print "creating clip from {0} to {1}".format(start,end)
    
    if os.path.isfile(mp4_file) == False:
        clip.write_videofile(mp4_file,fps=framerate)
        score += 0.5

    if os.path.isfile(gif_file) == False:
        clip.write_gif(gif_file,
                       fps=framerate,
                       program="ffmpeg")
        score += 0.5
    return score



class Film(object):
    """
    object that lets you talk to the directory as a nice object
    """
    root_dir = "F:\\internet_archive"
    clip_aim = 15

    @classmethod
    def populate_current(cls,rand=False):
        """
        given all current films - try and extract clips
        """
        def is_dir(di):
            return os.path.isdir(os.path.join(cls.root_dir,di))
        folders = [x for x in os.listdir(cls.root_dir) if is_dir(x)]
        
        if rand:
            folders = [random.choice(folders)]
            
        random.shuffle(folders)
        
        for f in folders:
            fi = cls(f)
            if fi.failed == False:
                fi.create_gifs()
                
  
    @classmethod          
    def find_films(cls,search_term="collection:(Feature_Films) AND mediatype:(movies)"):
        """
        download films and process
        """
        films = search_items(search_term)
        
        films = [x['identifier'] for x in films]
        
        random_group = random.sample(films,100)
        
        for t in random_group:
            print t
            try:
                fi = cls(t)
            except Exception:
                print "failure"
                fi = None
            if fi and fi.failed == False:
                fi.create_gifs()


    
    def __init__(self,ident):
        """
        set up directory info - download from archive if necessary
        """
        self.ident = ident
        self.dir = os.path.join(Film.root_dir,ident)
        self.clip_dir = os.path.join(self.dir,"clips")
        self.failed = False
        if os.path.isdir(self.dir) == False:
            item = get_item(ident)
            ogg = [x['name'] for x in item.files if ".ogv" in x['name']]
            meta = [x['name'] for x in item.files if "_meta.xml" in x['name']]
            if ogg and meta:
                ogg = ogg[:1]
                meta = meta[:1]
                os.makedirs(self.dir)
                os.makedirs(self.clip_dir)
                download(ident,files=ogg+meta,destdir=Film.root_dir, verbose=True)
            else:
                self.failed = True
        
        if self.failed == False:
            self.ogv = [x for x in os.listdir(self.dir) if ".ogv" in x]
            self.meta = [x for x in os.listdir(self.dir) if "_meta.xml" in x]
            
            if self.ogv and self.meta:
                self.ogv = self.ogv[0]
                self.meta =self.meta[0]
                self.load_meta()
            else:
                self.failed = True
            
            
            
    def clips(self):
        for f in os.listdir(self.clip_dir):
            if ".mp4" in f:
                yield f
        
    @classmethod
    def all_schedules(cls):
        """
        create all xls files and join as one
        """
        def is_dir(di):
            return os.path.isdir(os.path.join(cls.root_dir,di))
        folders = [x for x in os.listdir(cls.root_dir) if is_dir(x)]

        schedules = []
        for f in folders:
            fi = cls(f)
            schedules.append(fi.produce_schedule())
            
        ql = QuickList().union(schedules)
        ql.save("F:\\mp4s\joined.xls")
            
                        
        
    def produce_schedule(self):
        """
        moves files and creates a schedule
        """
        destination_path = "F:\\mp4s"
        ql = QuickList()
        ql.header = ["title",
                     "year",
                     "nice_title",
                     "film_ident",
                     "timestamp",
                     "original_name",
                     "file_name",
                     "delete",
                     "trim"]
        
        for x,c in enumerate(self.clips()):
            print c
            old_name = c
            seconds = float(c.replace(".mp4","").replace("clip_",""))
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            timestamp = "%d:%02d:%02d" % (h, m, s)            
            
            file_name = self.ident + "_{0}.mp4".format(x)
            
            shutil.copyfile(os.path.join(self.clip_dir,old_name),
                            os.path.join(destination_path,file_name))
            
            row = [self.title,
                   self.date,
                   self.nice_name,
                   self.ident,
                   timestamp,
                   old_name,
                   file_name,
                   "",
                   "",
                   ]
            ql.add(row)
            
            
        ql.save(os.path.join(self.dir,"schedule.xls"))
        return ql
                 
        
    def load_meta(self):
        """
        extract metadata from archive.org download - if possible
        """
        from xml.etree import ElementTree
        e = ElementTree.parse(os.path.join(self.dir,self.meta)).getroot()
        self.title = e.find('title').text
        try:
            self.date = e.find('date').text
        except AttributeError:
            self.date = ""
        
        if self.date:
            self.nice_name = u"{0} ({1})".format(self.title,self.date)
        else:
            self.nice_name = self.title
        
        try:    
            print self.nice_name
        except Exception:
            pass
        
        
            
    def finished_flag_loc(self):
        return os.path.join(self.dir,"processed.txt")

    def has_finished_flag(self):
        return os.path.isfile(self.finished_flag_loc())
            
    def ogv_loc(self):
        return os.path.join(self.dir,self.ogv)

    def deinterlaced_ogv_loc(self):
        
        deinter = self.ogv[:-4] + "_deinterlaced.ogv"
        return os.path.join(self.dir,deinter)
        
    def get_clip_total(self):
        """
        how many gifs have we produced?
        """
        return len([x for x in os.listdir(self.clip_dir) if ".mp4" in x])
        
    def create_gifs(self):
        """
        produce clips until we have more than our aim
        """
        returns = []
        if self.has_finished_flag() == False:
            while self.get_clip_total() < Film.clip_aim:
                count = self.process_scenes()
                returns.append(count)
                if len(returns) > 3 and sum(returns[-3:]) == 0:
                    print "giving up!"
                    break
            """
            create flag
            """
            with open(self.finished_flag_loc(), "w+") as f:
                pass


    def get_length(self):
        """
        how long is this video? requires ffprobe
        """
        result = subprocess.Popen(["ffprobe", self.ogv_loc()],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        st = [x for x in result.stdout.readlines() if "Duration" in x][0]
        duration = st.split(",")[0].split("Duration: ")[1].strip()
        hours,minutes,seconds = [float(x) for x in duration.split(":")]
        minutes += hours*60
        seconds += minutes*60
        
        return seconds
    
    def deinterlace(self):
        """
        runs file through vlc to deinterlace
        """
        options = ["C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc",
                   "--play-and-exit",
                   self.ogv_loc(),
                   '--video-filter="deinterlace"',
                   '--deinterlace-mode="blend"',
                   '--sout=file/ogg:{0}'.format(self.deinterlaced_ogv_loc())
                   ]
        result = subprocess.Popen(options,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.STDOUT)
        for l in result.stdout.readlines():
            print l
            

    def process_scenes(self):
        """
        pick a random five minutes to examine for scenes - then pass out to create gifs
        returns number of clips created
        """
        import scenedetect
        
        scene_list = []
        out_dir = self.clip_dir
        path = self.ogv_loc()
        
        detector_list = [
            scenedetect.detectors.ContentDetector(threshold = 5,min_scene_len=4)
            #scenedetect.detectors.ThresholdDetector(threshold = 16, min_percent = 0.9)
        ]
        
        random.seed()
        total_seconds = self.get_length()
        if total_seconds < 60*10:
            start = random.uniform(60,total_seconds-60) # ignore first and last five minutes
            timecode_list = [start,start+60.0,0]
        else:
            start = random.uniform(300,total_seconds-600) # ignore first and last five minutes
            timecode_list = [start,start+60*5.0,0]
        print "starting at {0}".format(start)
        
        if start < 0:
            return 0
        
        video_framerate, frames_read = scenedetect.detect_scenes_file(
            path, scene_list, detector_list,timecode_list=timecode_list)
        
        print "detected"
        scene_list_sec = [x / float(video_framerate) for x in scene_list]
        
        ten_frame_offset = (1/video_framerate) * 10
        
        def yield_pairs():
            last = None
            for s in scene_list_sec:
                if last:
                    if s-last <= 6 + ten_frame_offset*2 and s-last>=4: # max of six second scenes-
                        yield (last+ten_frame_offset,s-ten_frame_offset) #cut ten frames from start and end
                last = s
        
        clip_count = 0
        
        for start,end in yield_pairs():
            clip_count+= make_clip(path,out_dir,video_framerate,start,end)
        return clip_count
        
    

if __name__ == "__main__":
    pass
    #make_small_gif()
    #Film.populate_current()
    #Film.find_films()
    #Film.all_schedules()
    #create_preview_from_schedule()
    move_good_clips()
    #f = Film("GuestInTheHouse1944")
    #f.produce_schedule()
    #f.load_meta()
    #f.create_gifs()
    #make_clip("F:\internet_archive\GuestInTheHouse1944\\GuestInTheHouse1944_deinterlaced.ogv","F:\internet_archive\GuestInTheHouse1944\\",29.97,1148.18151485,1151)