from pathlib import Path
from json import load
import pygame


langs = ["en", "ru"]
lang_file = {}
for lang in langs:
    with open(Path(__file__).parent.resolve().with_name("assets").joinpath(f'lang/{lang}.json'),
              encoding='utf-8') as file:
        lang_file[lang] = load(file)


def format_number(number: int | float, places: int = 10) -> str:
    """Formats a number to a string with the specified number of decimal places.

    Parameters
    ----------
    number - the number to format.
    places - the number of decimal places to keep.

    Returns
    -------
    A string representation of the number with the specified number of decimal places.
    """
    if (isinstance(number, int) or int(number) == number) and len(str(int(number))) <= places:
        return str(int(number))
    if len(str(int(number))) >= places:
        return f"{number:,.1e}"
    return f"{number:,.{max(places-len(str(int(number))), 0)}f}"


def format_text(text: str, lang, *args):
    """Formats a string with the specified arguments.

    Parameters
    ----------
    text - the string to format.
    *args - the arguments to format the string with.

    Returns
    -------
    A formatted string.
    """
    new_args = [format_number(arg) if isinstance(arg, (int, float)) else loc(arg, lang) for arg in args]
    text = loc(text, lang)
    return text.format(*new_args)


def loc(text, lang):
    """Returns the localized string for the specified text and language.

    Parameters
    ----------
    text - the string to localize.
    lang - the language to localize the string to.

    Returns
    -------
    A localized string.
    """
    if lang in langs:
        if isinstance(text, str):
            dct = lang_file[lang]
            for key in text.split('.'):
                if key in dct:
                    dct = dct[key]
                else:
                    return text
            return dct
        elif isinstance(text, list):
            return loc(text[0], lang).format(*map(loc, text[1:], [lang]*(len(text)-1)))
    else:
        raise NotImplementedError("Localization not implemented for this language.")


def multiline_in_rect(string: str, font: pygame.font.Font, rect: pygame.rect.Rect,
                      font_color: tuple, bg_color: tuple, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Parameters
    ----------
    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rect style giving the size of the surface requested.
    fontColour - a three-byte tuple of the rgb value of the
             text color. ex (0, 0, 0) = BLACK
    BGColour - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                1 horizontally centered
                2 right-justified

    Returns
    -------
    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    final_lines = []
    requested_lines = string.splitlines()
    # Create a series of lines that will fit on the provided rectangle.
    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise Exception("The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size)
    surface.fill(bg_color)
    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise Exception("Once word-wrapped, the text string was too tall to fit in the rect.")
        if line != "":
            temp_surface = font.render(line, 1, font_color)
            if justification == 0:
                surface.blit(temp_surface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(temp_surface, ((rect.width - temp_surface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(temp_surface, (rect.width - temp_surface.get_width(), accumulated_height))
            else:
                raise Exception("Invalid justification argument: " + str(justification))
        accumulated_height += font.size(line)[1]
    return surface


def multiline(string: str, font: pygame.font.Font,
              font_color: tuple, bg_color: tuple = (0, 0, 0, 0), justification=0):
    """Returns a surface containing the passed text string, word-wrapping as necessary. The text
    will be anti-aliased, the rect will generate to fit the text.

    Parameters
    ----------
    string - the text you wish to render. \n begins a new line.
    font - a Font object
    font_color - a three-byte tuple of the rgb value of the
             text color. ex (0, 0, 0) = BLACK
    bg_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                1 horizontally centered
                2 right-justified

    Returns
    -------
    Success - a surface object with the text rendered onto it.
    Failure - raises an Exception if the text won't fit onto the surface.
    """

    requested_lines = string.splitlines()

    accumulated_height = 0
    max_width = 0
    surfaces = []
    for line in requested_lines:
        if line != "":
            temp_surface = font.render(line, 1, font_color)
            max_width = max(max_width, temp_surface.get_width())
            surfaces.append(temp_surface)
        else:
            surfaces.append(None)
        accumulated_height += font.size(line)[1]
    # Let's try to write the text out on the surface.
    surface = pygame.Surface((max_width, accumulated_height), pygame.SRCALPHA)
    surface.fill(bg_color)
    for i, tmp_surface in enumerate(surfaces):
        if tmp_surface:
            if justification == 0:
                surface.blit(tmp_surface, (0, i * font.get_height()))
            elif justification == 1:
                surface.blit(tmp_surface, ((max_width - tmp_surface.get_width()) / 2, i * font.get_height()))
            elif justification == 2:
                surface.blit(tmp_surface, (max_width - tmp_surface.get_width(), i * font.get_height()))
            else:
                raise Exception("Invalid justification argument: " + str(justification))
    return surface
