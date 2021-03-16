from notion.client import NotionClient
from notion.block import BasicBlock, HeaderBlock, QuoteBlock, TextBlock

client = NotionClient(token_v2 = 'b5bc62b3b2f0c274a73a4a482600c3a3ab33de2770c4ebeb910bbc5d6b01c4d89c356b9fc6b09e5a112c81ff5a9605502c705bc67476d4cc78977d2ed36137c3bfd69519239816b1c11cb6ec5fe1')
page = client.get_block("https://www.notion.so/potato-91fd9997532841feb0f5bde09fe36b45")

for child in page.children:
    print(child.title)

child = page.children.add_new(HeaderBlock, title='BAKEMONOGATARI ')
child = child.children.add_new(QuoteBlock, title='Pudim \n potato ')