import tkinter as tk
import pygame
from pytube import YouTube
import io
import requests
from ytmusicapi import YTMusic
from pydub import AudioSegment
from pydub.playback import play
from PIL import Image, ImageTk

class YouTubeMusicPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("YouTube Music Player")

        self.label = tk.Label(master, text="Enter Song Title:")
        self.label.pack()

        self.song_entry = tk.Entry(master, width=40)
        self.song_entry.pack()

        self.info_button = tk.Button(master, text="Get Song Info", command=self.get_song_info)
        self.info_button.pack()

        self.play_button = tk.Button(master, text="Play", command=self.play_song)
        self.play_button.pack()

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_song)
        self.stop_button.pack()

        self.info_text = tk.Text(master, height=10, width=50)
        self.info_text.pack()

        self.thumbnail_label = tk.Label(master)
        self.thumbnail_label.pack()

        # Initialize pygame mixer
        pygame.mixer.init()

        # Variable to store the currently playing audio stream URL
        self.current_sound = None

    def get_song_info(self):
        query = self.song_entry.get()
        if query:
            ytmusic = YTMusic()
            search_results = ytmusic.search(query)
            if search_results:
                first_result = search_results[0]
                title = first_result.get('title', 'Unknown Title')
                artist = ', '.join(artist['name'] for artist in first_result.get('artists', []))
                album = first_result.get('album', {}).get('name', 'Unknown Album')

                info_text = f"Title: {title}\nArtist(s): {artist}\nAlbum: {album}"
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, info_text)

                # Display thumbnail
                thumbnail_url = first_result.get('thumbnails', [{}])[0].get('url')
                if thumbnail_url:
                    image = self.load_image_from_url(thumbnail_url)
                    self.thumbnail_label.configure(image=image)
                    self.thumbnail_label.image = image

    def load_image_from_url(self, url):
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        img = img.resize((100, 100), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def get_audio_stream_url(self, video_id):
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            youtube = YouTube(youtube_url)
            audio_stream = youtube.streams.filter(only_audio=True).first()
            return audio_stream.url
        except Exception as e:
            print(f"Error: {e}")
            return None

    def play_song(self):
        query = self.song_entry.get()
        if query:
            ytmusic = YTMusic()
            search_results = ytmusic.search(query)
            if search_results:
                first_result = search_results[0]

                # Print the result for debugging
                print("First Result:", first_result)

                # Extract the video ID using different keys for different result types
                video_id = None
                if 'videoId' in first_result:
                    video_id = first_result['videoId']
                elif 'videoRenderer' in first_result:
                    video_id = first_result['videoRenderer'].get('videoId')
                elif 'videoRenderer' in first_result.get('sectionListRenderer', {}).get('contents', [{}])[0]:
                    video_id = first_result['sectionListRenderer']['contents'][0]['videoRenderer'].get('videoId')
                elif 'resultType' in first_result and first_result['resultType'] == 'song':
                    video_id = first_result.get('videoId')

                if video_id:
                    audio_stream_url = self.get_audio_stream_url(video_id)

                    if audio_stream_url:
                        # Stop the currently playing sound, if any
                        self.stop_song()

                        # Load the audio as a Sound object
                        self.current_sound = pygame.mixer.Sound(io.BytesIO(requests.get(audio_stream_url).content))

                        # Play the audio
                        self.current_sound.play()
                    else:
                        print("Error: Unable to extract audio stream URL.")
                else:
                    print("Error: Unable to extract videoId.")
            else:
                print("Error: No search results found.")
        else:
            print("Error: Please enter a song title.")

    def stop_song(self):
        if self.current_sound:
            self.current_sound.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeMusicPlayer(root)
    root.mainloop()
