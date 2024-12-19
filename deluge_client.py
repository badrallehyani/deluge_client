import random
import json, requests


def get_options(download_location,
                add_paused = False, sequential_download = False,
                pre_allocate_storage = False, move_completed = False,
                move_completed_path = "", max_connections = -1,
                max_download_speed = -1, max_upload_slots = -1,
                max_upload_speed = -1, prioritize_first_last_pieces = False, 
                seed_mode = False, super_seeding = False
                ):
    
    options = {
            "file_priorities": [
                1
            ],
            "add_paused": add_paused,
            "sequential_download": sequential_download,
            "pre_allocate_storage": pre_allocate_storage,
            "download_location": download_location,
            "move_completed": move_completed,
            "move_completed_path": move_completed_path,
            "max_connections": max_connections,
            "max_download_speed": max_download_speed,
            "max_upload_slots": max_upload_slots,
            "max_upload_speed": max_upload_speed,
            "prioritize_first_last_pieces": prioritize_first_last_pieces,
            "seed_mode": seed_mode,
            "super_seeding": super_seeding
    }

    return options

class MyDelugeClient:
    def __init__(self, host, port = 8112):
        self.base_url = f"http://{host}:{port}"
        self.json_url = self.base_url + "/json"

    def login(self, password):
        data = {
            "id": random.randint(1, 100),
            "method": "auth.login",
            "params": [password]
        }

        self.session = requests.session()
        response: dict = self.session.post(self.json_url, json = data).json()

        return response

    def add_download(self, download_url, download_location, **options):
        options = get_options(download_location, **options)

        req_id = random.randint(1,10)

        response: dict = self.send_download_torrent_from_url(download_url, req_id)
        if(response.get('error') != None):
            raise Exception("Error " + str(response))
        
        tmp_file_dir = response.get("result")


        torrent_info = self.send_get_torrent_info(tmp_file_dir, req_id + 1)
        if( not torrent_info.get('result') ):
            raise Exception("Invalid Torrent File")

        return self.send_add_torrent(tmp_file_dir, options, req_id + 2)
    

    def send_add_torrent(self, file_dir, options, req_id):
        data = {
            "method": "web.add_torrents",
            "params":[
                [
                    {
                        "path": file_dir,
                        "options": options
                    }
                ]
            ],

            "id": req_id
        }
        response = self.session.post(self.json_url, json = data, timeout = 5).json()
        return response


    def send_download_torrent_from_url(self, download_url, req_id):
        data = {
            "method": "web.download_torrent_from_url",
            "params": [
                download_url,
                ""
            ],
            "id": req_id
        }

        response = self.session.post(self.json_url, json = data).json()
        return response
    
    def send_get_torrent_info(self, file_dir, req_id):
        data = {
            "method": "web.get_torrent_info",
            "params": [
                file_dir
            ],
            "id": req_id
        }

        response: dict = self.session.post(self.json_url, json = data).json()
        return response
