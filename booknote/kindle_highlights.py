class Highlights:
    
    def get_kindle_highlights(self, kindle_path:str = '/Volumes/Kindle') -> list:
        """Read and parse the Highlights from the user's kindle device

        Args:
            kindle_path (str, optional): The path to the mounter kindle device. Defaults to '/Volumes/Kindle'.

        Returns:
            list: The json formatted Highlights 
        """        
        self.path = kindle_path
        return self.__parse_file()

    def __parse_file(self) -> list:
        """Parse and format the MyClippings.txt file from the kindle

        Returns:
            list: format the contents of the file in json
        """            
        # Read the file that contains the kindle's highlights 
        with open(self.path+'/documents/My Clippings.txt', 'r') as data_file:
            data = data_file.read()
            data = data.split('==========')

        # Now that we have a list of highlights, we can make a list of dictionaries to dissect the structure of the saved data 
        quotes = []
        for quote in data:
            quote = quote.splitlines()
            try:
                quote_structure = {'book title':quote[1], 'book location':quote[2], 'quote':quote[4]}
                quotes.append(quote_structure)
                print(quote_structure)
                print('#' * 10)
            except:
                continue

        # Now we can return the list of quotes 
        return quotes
        



if __name__ == '__main__':
    highlights = Highlights()
    quotes = highlights.get_kindle_highlights()

