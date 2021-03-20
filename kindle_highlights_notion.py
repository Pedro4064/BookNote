from notion.client import NotionClient
from notion.block import BulletedListBlock, DividerBlock, SubheaderBlock, QuoteBlock, TextBlock
from kindle_highlights import Highlights

import json
import os 

class TimeCapsule:

    def set_up_notion_credentials(self, token_v2:str, page_url:str) -> None:
        
        # Create the config file and store the inforation for future reference 
        with open('notion.config', 'w') as config_file:
            data = {'token_v2': token_v2, 'page_url':page_url}
            config_file.write(json.dumps(data, indent=4))


    def load_notion_credentials(self) -> None:
        
        # try to read the config file to load the information, if it fails to open, most probably there is no file
        try:
            with open('notion.config', 'r') as config_file:
                self.credentials = json.loads(config_file.read())

        except:
            raise "[ERROR] Notion config file not Set Up"


    def get_kindle_highlights(self, only_new:bool = True)->list:

        # Get the data from the kindle .txt file 
        kindle = Highlights()
        self.highlights = kindle.get_kindle_highlights()

        # Read the log file
        old_data = self.__load_last_kindle_data()


        # Now that we have the data, we can save to the log for the next time before changing the variables
        with open('kindle.log', 'w') as log_file:
            log_file.write(json.dumps(self.highlights, indent=4))

        # If the argument `only_new` is set to true, we first need to parse the data before uploading to notion 
        # So we first need to load the data from the last kindle check
        if only_new:

            # only keep the new data during the list comprehention 
            self.highlights = [highlight for highlight in self.highlights if highlight not in old_data] 

            
        # If they want all the data, simply don't change the self.highlights variable 
        return self.highlights


    def upload_highlights(self, subcategories:bool = True)-> None:
        
        # To upload the highlights to notion we first need to initialize the notion API
        self.__initialize_notion_api()
        
        # No that we have initialized, we can upload, but first we need to check rather the user wants to upload 
        # the quotes in  subcategories (i.e all the quotes from one book as sublocks to the book title) or 
        # just save the each quote with their own title on their own block.
        if subcategories:
            # Since the user chose to save in subcategories, we first need to separate each highlight by their book

            # We first get all the book titles form each and every entry  
            book_titles = [entry['book title'] for entry in self.highlights]

            # Then we create a dictionary with the titles as keys (there will be no repetition) with the value of an empty list
            ordered_highlights = dict.fromkeys(book_titles, [])
            
            # Now we can populate every list with a quote
            for key in ordered_highlights:
                ordered_highlights[key] = [entry for entry in self.highlights if entry['book title'] == key]
            

            # Now that we have the quotes separated by their book title, we can upload the data 
            self.__populate_notion(ordered_highlights)
    

    def __initialize_notion_api(self):

        self.client = NotionClient(token_v2 = self.credentials['token_v2'])
        self.page = self.client.get_block(self.credentials['page_url'])


    def __populate_notion(self, highlights:dict):
        
        # Set the color of the blocks 
        header_color = 'pink'
        location_color = 'gray'

        # Get a list of all title already on the page 
        notion_titles = [child.title for child in self.page.children]

        for title in highlights:
            
            # First we need to check rather or not the book already has an entry 
            if title not in notion_titles:
                # Since there are no previous entries, we can simply add the title and the quote at the end of the page
                self.page.children.add_new(SubheaderBlock, title=title, color=header_color)
                for quote in highlights[title]:
                    self.page.children.add_new(QuoteBlock, title=quote['quote'])
                    self.page.children.add_new(BulletedListBlock, title=quote['book location'].replace('-',''), color=location_color)
                    self.page.children.add_new(DividerBlock)

                # Add the titles to the notion_titles now that we have added it no notion 
                notion_titles.append(title)
                
            else:
                self.title = title
                # If it is not the first entry, we must find the block corresponding to the title block to that book
                header_block = list(filter(self.__filter_children, self.page.children))[0]

                # Now that we have the parent block, we can iterate through the quotes and add them
                for quote in highlights[title]:
                    quote_block = self.page.children.add_new(QuoteBlock, title=quote['quote'])
                    page_info_block = self.page.children.add_new(BulletedListBlock, title=quote['book location'].replace('-',''), color=location_color)
                    divider_block = self.page.children.add_new(DividerBlock)

                    # Now move the blocks to the correct location 
                    quote_block.move_to(header_block, 'after')
                    page_info_block.move_to(quote_block, 'after')
                    divider_block.move_to(page_info_block, 'after')


    def __filter_children(self, child) -> bool:

        try:
            if child.title == self.title:
                return True
        except:
            return False


    def __load_last_kindle_data(self):
        
        try:
            with open('kindle.log', 'r') as log_file:

                data = json.loads(log_file.read())
                return data

        except:
            return []


if __name__ == '__main__':

    vault = TimeCapsule()
    vault.set_up_notion_credentials(token_v2='****', page_url="*****")
    vault.load_notion_credentials()

    highlights = vault.get_kindle_highlights()
    vault.upload_highlights()
