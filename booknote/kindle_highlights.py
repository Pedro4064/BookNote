import json 

class Highlights:
    
    def get_kindle_highlights(self, kindle_path:str = '/Volumes/Kindle'):
        self.path = kindle_path
        return self.__parse_file()

    def __parse_file(self):
        
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

