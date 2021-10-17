from notion.client import NotionClient
from notion.block import BulletedListBlock, DividerBlock,HeaderBlock , SubheaderBlock, SubsubheaderBlock, QuoteBlock, TextBlock, TodoBlock, PageBlock, CalloutBlock, ToggleBlock
from booknote.kindle_highlights import Highlights

from sys import platform
import json
import os 

class NotionCredentialError(Exception):
    pass

class TimeCapsule:

    def __init__(self):
        # Set basic variables
        self.config_file = './booknote/config/config.json'
        self.style_file  = './booknote/config/style.json'
        self.kindle_log  =  './booknote/config/kindle.log'

        # Set variables for future comparison
        self.logged_highlights = []
        self.kindle_highlights = []
        self.new_highlights = []

        # Load the necessary information
        try:
            self.config_values = self.__load_file(self.config_file)
        except:
            self.__generate_config_file()
        
        try:
            self.style_values = self.__load_file(self.style_file)
        except:
            self.__generate_style_file()
        
    def config(self,name:str, value:str) -> None:
        # First and foremost we need to check if we the config file is already in our system
        if (not self.__file_exists(self.config_file)):
            self.__generate_config_file()

            data = self.__load_file(self.config_file)
            data[name] = value 

            self.__write_file(self.config_file, data)
        
        # If the config is already in the system, load it to change the data in it and save it back
        else:
            config_data = self.__load_file(self.config_file)
            config_data[name] = value
            self.__write_file(self.config_file, config_data)

    def style(self,element:str, variable:str, value:str) -> None:
        # First and foremost we need to check if we the style file is already in our system
        if (not self.__file_exists(self.style_file)):
            self.__generate_style_file()

            data = self.__load_file(self.style_file)
            data[element][variable] = value

            self.__write_file(self.style_file, data)
        
        # If the config is already in the system, load it to change the data in it and save it back
        else:
            style_data = self.__load_file(self.style_file)
            style_data[element][variable] = value
            self.__write_file(self.style_file, style_data)

    def __file_exists(self, name:str) -> bool:
        if (name not in os.listdir()):
            return False
        
        else:
            return True
        
    def __generate_config_file(self) -> None:
            
        data = {'notion.v2token':'',
                'notion.page':'',
                'kindle.location': '/Volumes/Kindle' if platform=='darwin' else '/media/Kindle',
                'kindle.log': self.kindle_log}

        self.__write_file(file_name = self.config_file, data = data, overwrite=True)

    def __generate_style_file(self) -> None:
            
        data = {'title': {'color':'pink', 'block.type':'SubheaderBlock'},
                'quote': {'color':'default', 'block.type':'QuoteBlock'},
                'annotation': {'color':'gray', 'block.type':'BulletedListBlock'}}

        self.__write_file(file_name = self.style_file, data = data, overwrite=True)
         
    def __load_file(self, file_name:str) -> dict:
        with open(file_name, 'r') as f:
            return json.loads(f.read())

    def __write_file(self, file_name:str, data:dict, overwrite:bool = True):
            mode = 'w' if overwrite else 'a'

            with open(file_name, mode) as f:
                f.write(json.dumps(data, indent=4))

    def get_kindle_highlights(self, only_new:bool = True)->list:
        
        # Get the data from the kindle .txt file 
        kindle = Highlights()
        self.kindle_highlights = kindle.get_kindle_highlights(self.config_values['kindle.location'])

        # Read the log file, create an populate with empty json if does not exist
        if (not self.__file_exists(self.kindle_log)):
            self.logged_highlights = []
            self.__write_file(self.kindle_log, self.logged_highlights)
        else:
            self.logged_highlights = self.__load_file(self.kindle_log)

        # If the argument `only_new` is set to true, we first need to parse the data before uploading to notion 
        # So we first need to load the data from the last kindle check
        if only_new:
            # only keep the new data during the list comprehention 
            self.new_highlights = [highlight for highlight in self.kindle_highlights if highlight not in self.logged_highlights] 

            
        return self.kindle_highlights if only_new else self.kindle_highlights

    def upload_highlights(self, highlights:list)-> None:
        
        # To upload the highlights to notion we first need to initialize the notion API, if it fails 
        self.__initialize_notion_api()

    
        # First need to separate each highlight by their book
        # We first get all the book titles form each and every entry  
        book_titles = [entry['book title'] for entry in highlights]

        # Then we create a dictionary with the titles as keys (there will be no repetition) with the value of an empty list
        ordered_highlights = dict.fromkeys(book_titles, [])
        
        # Now we can populate every list with a quote
        for key in ordered_highlights:
            ordered_highlights[key] = [entry for entry in highlights if entry['book title'] == key]
        

        # Now that we have the quotes separated by their book title, we can upload the data 
        self.__populate_notion(ordered_highlights)

        # And at last we can save the data to the kindle file 
        self.__write_file(self.kindle_log, self.kindle_highlights)

    def __initialize_notion_api(self):
        try:
            self.client = NotionClient(token_v2 = self.config_values['notion.v2token'])
            self.page = self.client.get_block(self.config_values['notion.page'])
        except:
            raise NotionCredentialError()

    def __populate_notion(self, highlights:dict):
        
        # Set the types of blocks
        types = {'HeaderBlock': HeaderBlock, 'SubheaderBlock': SubheaderBlock, 'SubsubheaderBlock': SubsubheaderBlock, 'QuoteBlock': QuoteBlock, 'TextBlock': TextBlock, 'PageBlock': PageBlock,'BulletedListBlock':BulletedListBlock ,'TodoBlock': TodoBlock, 'CalloutBlock': CalloutBlock, 'ToggleBlock': ToggleBlock}
        
        header_type = types[self.style_values['title']['block.type']]
        location_type = types[self.style_values['annotation']['block.type']]
        quote_type = types[self.style_values['quote']['block.type']]
        
        # Set the color of the blocks 
        header_color = self.style_values['title']['color']
        location_color = self.style_values['annotation']['color']
        quote_color = self.style_values['quote']['color']

        # Get a list of all title already on the page 
        notion_titles = []
        for child in self.page.children:
            try:
                notion_titles.append(child.title)
            except:
                continue 

        print(notion_titles)

        for title in highlights:
            
            # First we need to check rather or not the book already has an entry 
            if title not in notion_titles:
                # Since there are no previous entries, we can simply add the title and the quote at the end of the page
                header_block = self.page.children.add_new(header_type, title=title, color=header_color)
                for quote in highlights[title]:
                    quote_block = self.page.children.add_new(quote_type, title=quote['quote'], color=quote_color)
                    page_info_block = self.page.children.add_new(location_type, title=quote['book location'].replace('-',''), color=location_color)
                    divider_block = self.page.children.add_new(DividerBlock)

                    # Now, if the header block is either a page or a toggle, move the blocks to the correct location 
                    if self.style_values['title']['block.type'] == 'ToggleBlock' or self.style_values['title']['block.type'] == 'PageBlock':
                        quote_block.move_to(header_block, "last-child")
                        page_info_block.move_to(header_block, "last-child")
                        divider_block.move_to(header_block, "last-child")


                # Add the titles to the notion_titles now that we have added it no notion 
                notion_titles.append(title)
                
            else:
                self.title = title
                # If it is not the first entry, we must find the block corresponding to the title to that book
                header_block = list(filter(self.__filter_children, self.page.children))[0]

                # Now that we have the parent block, we can iterate through the quotes and add them
                for quote in highlights[title]:
                    quote_block = self.page.children.add_new(quote_type, title=quote['quote'], color=quote_color)
                    page_info_block = self.page.children.add_new(location_type, title=quote['book location'].replace('-',''), color=location_color)
                    divider_block = self.page.children.add_new(DividerBlock)

                    # Now move the blocks to the correct location 
                    quote_block.move_to(header_block, "last-child")
                    page_info_block.move_to(quote_block, "last-child")
                    divider_block.move_to(page_info_block, "last-child")

    def __filter_children(self, child) -> bool:

        try:
            if child.title == self.title:
                return True
        except:
            return False



if __name__ == '__main__':
    
    vault = TimeCapsule()
    vault.style('title', 'block.type', 'PageBlock')

    # # vault.set_up_notion_credentials(token_v2='****', page_url="*****")
    # vault.load_notion_credentials()

    # highlights = vault.get_kindle_highlights()
    # vault.upload_highlights()
