import click
from click.decorators import pass_context
from kindle_highlights_notion import NotionCredentialError, TimeCapsule

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = TimeCapsule()
    

@cli.command()
@click.argument('name')
@click.argument('value')
@click.pass_obj
def config(capsule, name, value):
    """Change the configuration variables for the program

    
    Variables

    \b
        kindle.log
            The locaton for the kindle.log file, responsable for keeping track of the already uploaded Highlights
        
        kindle.path
            The path to where the kindle device is mounted, defaults to `/Volumes/Kindle` on MacOS
        
        notion.page
            The Url for the notion page you want the Highlights to be stored
        
        notion.v2token
            The V2 token for authentication
    
    \b 

    Extra Resources 

    \b 
        Token V2
            To get the v2 token from notion, follow this tutorial: https://www.redgregory.com/notion/2020/6/15/9zuzav95gwzwewdu1dspweqbv481s5
    """
    capsule.config(name, value)

@cli.command()
@click.argument('element')
@click.argument('variable')
@click.argument('value')
@click.pass_obj
def setstyle(capsule, element, variable ,value):
    """Change the style variables for the Notion Page Formatting

    
    Elements

    \b
        title
            The block for the books titles
    \b  
        quote
            The block for the contentes of the kindle's highlights
        
        annotation
            The block for other annotations, such as the highlights location in the book
        
    \b 

    Variables 

        There are 2 variables:

    \b
        color
            The color of the block (gray|brown|orange|yellow|green|blue|purple|pink|red)
    
    \b
        block.type
            The type of block the element will be rendered as in the Notion page
            (HeaderBlock|SubheaderBlock|SubsubheaderBlock|QuoteBlock|TextBlock|PageBlock|BulletedListBlock|TodoBlock|CalloutBlock|ToggleBlock)

    Example

    \b 
        booknote setstyle title block.type HeaderBlock
    """
    capsule.style(element, variable, value)


@cli.command()
@click.option('--all', default=False, help="Upload all the Kindle's Highlights, NOT only the new ones")
@click.pass_obj
def upload(capsule, all):
    """Upload to Notion the Highlights on the kindle

    """
    # Get the highlights on the system, and if the user wants to only get the new ones or all of them
    highlights = capsule.get_kindle_highlights(only_new = not all)

    # Now try to upload
    try: 
        capsule.upload_highlights(highlights)
    
    except NotionCredentialError:
            click.echo('[ERROR] There was an error during the upload, make sure your config information is correct by running: notebook list config')


if __name__ == '__main__':
    cli()