import os
import yaml

from utils.mode import MODE
from utils.source_type import TYPE
from utils.logger import Logger



class config:

    # TODO: in every function, make sure you've gotten the right input args
    sources = []
    mode = MODE.DEFAULT
    executable = ''
    series_info = dict()
    logger = Logger('config')

    def __init__(self, srcs_filename, cfg_filename):
        # first read the acceptable sources
        self.sources = self.read_sources(srcs_filename)

        # read the user's configuration file
        user_cfg_data = self.read_user_config_file(cfg_filename)

        # after opening the file, parse the fields and/or replace with default
        self.mode = self.parse_mode(user_cfg_data)
        self.executable = self.parse_executable(user_cfg_data)
        
        # parse the series in there
        self.series_info = self.parse_series_list(user_cfg_data, self.sources)

    def read_sources(self, filepath):
        #filepath = '%s%s..%ssources.yaml' % \
        #    (os.path.dirname(os.path.abspath(__file__)), os.path.sep, os.path.sep)
        try:
            with open(filepath,'r') as file:
                data = yaml.safe_load(file)
                data_dict = dict()
                for idx,val in enumerate(data):
                    val_id = val.pop('id')
                    data_dict[val_id] = val
                return data_dict
        except:
            errno = 'LHconfig::SourceReadError'
            txt = "Source list cannot be found."
            self.logger.error("%s::" % (errno, txt))
            raise Exception("%s::" % (errno, txt))

    def read_user_config_file(self, user_cfg_filename):
        try:
            with open(user_cfg_filename,'r') as file:
                data = yaml.safe_load(file)
                return data
        except:
            errno = 'LHconfig::UserCfgReadError'
            txt = "User's configuration file (%s) is not formatted properly. Must be a valid YAML file" % (user_cfg_filename,)
            self.logger.error("%s::" % (errno, txt))
            raise Exception("%s::" % (errno, txt))

    def parse_mode(self, user_mode):
        if 'mode' in user_mode:
            user_mode = user_mode['mode']
        
        program_mode = MODE.DEFAULT
        try:
            program_mode = MODE[user_mode.upper()]
        except:
            pass # leave program_mode as DEFAULT
    
        return program_mode

    def parse_series_list(self, user_series_list, sources):
        series = []

        if 'series' in user_series_list:
            user_series_list = user_series_list['series']

        for idx,val in enumerate(user_series_list):
            title = val['title']
            if len(title) == 0:
                errno = 'LHconfig::TitleEmpty'
                txt = 'series #%d is empty' % (idx)
                self.logger.error("%s::" % (errno, txt))
                raise Exception("%s::" % (errno, txt))
            
            if title in self.series_info.keys():
                errno = 'LHconfig::TitleError'
                txt = 'series #%d already exists' % (idx)
                self.logger.error("%s::" % (errno, txt))
                raise Exception("%s::" % (errno, txt))
            
            authors = self.parse_authors(user_series_list)
            
            source_type = self.parse_type(val)

            meta = self.parse_meta(val)
            
            source = self.parse_source(val, sources)
            
            # recursively verify existance
            savepath = self.parse_savepath(val)

            # parse the target chapters to scrape
            target_chapters = self.parse_chapters(val)
            target_chapters = self.filter_chapter_range(target_chapters, savepath, title)

            # parse the series
            target_volumes = self.parse_volumes(val)
            
            series.append(dict(\
                title=title, \
                authors=authors, \
                type=source_type, \
                meta=meta, \
                source=source, \
                savepath=savepath, \
                chapters=target_chapters, \
                volumes=target_volumes))
        
        return series

    def parse_type(self, user_type):
        if 'type' in user_type:
            user_type = user_type['type']
        
        try:
            return TYPE[user_type.upper()]
        except:
            errno = 'LHconfig::UserCfgTypeError'
            txt = "User's configuration file has a an invalid TYPE"
            self.logger.error("%s::" % (errno, txt))
            raise Exception("%s::" % (errno, txt))

    def parse_meta(self, meta_data):
        meta = ''
        if 'meta' in meta_data:
            meta = meta_data['meta']
        
        return meta


    def parse_source(self, user_source, sources):
        if 'source' in user_source:
            user_source = user_source['source']
        
        if user_source.lower() not in sources.keys():
            errno = 'LHconfig::UserCfgSourceError'
            txt = "User's configuration file has a source (%s) that isn't among the list of valid sources" % (user_source,)
            self.logger.error("%s::" % (errno, txt))
            raise Exception("%s::" % (errno, txt))
        
        return user_source.lower()
    
    def parse_savepath(self, user_savepath):
        if 'savepath' in user_savepath:
            user_savepath = user_savepath['savepath']
        
        real_savepath = os.path.abspath(user_savepath)
        # TODO: make sure the path is valid
        folders = real_savepath.split(os.path.sep)

        # recursively look for this directory (all the way up to watchtower)
        # if it doesn't exist, make it
        existing_dir = ''
        existing_dir_idx = -1
        for i in range(len(folders), 0, -1):
            testpath = os.path.sep.join(folders[0:i])
            if os.path.exists(testpath):
                existing_dir = testpath
                existing_dir_idx = i
                break
        
        # make sure we found an existing dir
        if not existing_dir:
            # did not find an existing sub-path in the savepath
            errno = 'LHconfig::UserCfgSavepathError'
            txt = "User's configuration file has a savepath (%s) that doesn't have an existing folder" % (real_savepath,)
            self.logger.error("%s::" % (errno, txt))
            raise Exception("%s::" % (errno, txt))

        if not os.path.exists(real_savepath):
            os.makedirs(real_savepath)

        return real_savepath

    def parse_chapters(self, user_chapters):
        target_chapters = dict(\
            start=0, \
            stop=float('inf'), \
            scrape_range=[],
            package_range=[])
        
        if 'chapters' in user_chapters:
            user_chapters = user_chapters['chapters']
        
        if 'start' in user_chapters:
            if isinstance(user_chapters['start'], str):
                target_chapters['start'] = float(user_chapters['start'])
            elif isinstance(user_chapters['start'], int):
                target_chapters['start'] = user_chapters['start']
            else:
                raise Exception('bad integer value....')
        
        if 'stop' in user_chapters:
            if isinstance(user_chapters['stop'], str):
                target_chapters['stop'] = float(user_chapters['stop'])
            elif isinstance(user_chapters['stop'], int):
                target_chapters['stop'] = user_chapters['stop']
            else:
                raise Exception('bad integer value....')
        if target_chapters['stop'] < float('inf'):
            target_chapters['scrape_range'] = list(range(target_chapters['start'],target_chapters['stop']+1))
            target_chapters['package_range'] = list(range(target_chapters['start'],target_chapters['stop']+1))
        return target_chapters
    
    def filter_chapter_range(self, target_chapters, savepath, title):
        if not os.path.isdir(os.path.sep.join([savepath,title,'raws'])):
            return target_chapters
        
        files = os.listdir(os.path.sep.join([savepath,title,'raws']))
        for file in files:
            myid = file.split('.')[0]
            if myid != 'authors':
                myid = int(myid)
                target_chapters['scrape_range'].pop(target_chapters['scrape_range'].index(myid))
        return target_chapters

    def parse_volumes(self, user_volumes):
        volumes = []
        if 'volumes' in user_volumes:
            user_volumes = user_volumes['volumes']
        
        for i in range(len(user_volumes)):
            volume = dict(\
                name='', \
                photos=self.parse_photos(user_volumes[i]), \
                chapters=self.parse_chapters(user_volumes[i]))
            
            if 'name' in user_volumes[i]:
                volume['name'] = user_volumes[i]['name']
            
            volumes.append(volume)
        
        return volumes
    
    def parse_photos(self, user_photos):
        photos = dict(\
            front_cover='', 
            illustration='', 
            map='',
            back_cover='')
        
        if 'photos' in user_photos:
            user_photos = user_photos['photos']
        
        if 'front_cover' in user_photos:
            photos['front_cover'] = user_photos['front_cover']
        if 'illustration' in user_photos:
            photos['illustration'] = user_photos['illustration']
        if 'back_cover' in user_photos:
            photos['back_cover'] = user_photos['back_cover']

        return photos

    def parse_executable(self, exec):
        if 'executable' in exec:
            return exec['mode']
        else:
            return ''

    def parse_authors(self, authors):
        if 'content_author' in authors:
            return authors['authors']
        else:
            return ['']

    def get_dict(self):
        return dict(sources=self.sources, mode=self.mode, series=self.series_info, executable=self.executable)
