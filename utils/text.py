from json import load
import re
from math import isclose
import pygame
import game_context
from config import asset_path


langs = ["en", "ru"]
lang_file = {}
for l in langs:
    with open(asset_path.joinpath(f'lang/{l}.json'),
              encoding='utf-8') as file:
        lang_file[l] = load(file)


def format_number(number: int | float | str, places: int = 8) -> str:
    """Formats a number to a string with the specified number of decimal places.

    Parameters
    ----------
    number - the number to format.
    places - the number of decimal places to keep.

    Returns
    -------
    A string representation of the number with the specified number of decimal places.
    """
    if isinstance(number, str):
        try:
            number = float(number)
        except ValueError:
            return number
    s_int = str(int(number))
    if isinstance(number, int) or isclose(number, int(number)):
        if len(s_int) <= places:
            return s_int
        else:
            return f"{number:.1e}"

    abs_n = abs(number)
    if abs_n < 10:
        s = f"{number:.2f}"
    elif abs_n < 100:
        s = f"{number:.1f}"
    else:
        s = str(int(number))

    if "." in s:
        s = s.rstrip("0").rstrip(".")

    if len(s) > places:
        s = f"{number:.1e}"
    return s


def format_text(text: str, *args):
    """Formats a string with the specified arguments.

    Parameters
    ----------
    text - the string to format.
    *args - the arguments to format the string with.

    Returns
    -------
    A formatted string.
    """
    new_args = [format_number(arg) if isinstance(arg, (int, float)) else loc(arg) for arg in args]
    text = loc(text)
    return text.format(*new_args)


def format_card_description(text: str, effects, flags):
    """Formats a card description with the card's effects and flags.
    &[flag_name] is replaced with flags['flag_name']
    #[effect_name.param] is replaced with effects: effect['name'] == effect_name: effect['params'][param] or effect['param']

    Parameters
    ----------
    text - the string to format.
    effects - the effects of the card.
    flags - the flags of the card.

    Returns
    -------
    A formatted string.
    """
    flags_names = re.findall(r"&\[(.*?)\]", text)
    for flag in flags_names:
        if flag in flags:
            text = text.replace(f"&[{flag}]", str(format_number(flags[flag])))
        else:
            text = text.replace(f"&[{flag}]", "")
    params = re.findall(r"#\[(.*?)\]", text)
    for param in params:
        effect_name, param_name = param.split('.')
        to_ret = ""
        for effect in effects:
            if effect["name"] == effect_name:
                if param_name in effect:
                    to_ret = str(format_number(effect[param_name]))
                elif param_name.isdigit() and int(param_name) < len(effect["params"]):
                    to_ret = str(format_number(effect["params"][int(param_name)]))
                else:
                    to_ret = ""
                break
        text = text.replace(f"#[{param}]", to_ret)
    percentages = re.findall(r"(\d+(?:\.\d+)?)%", text)
    for percentage in percentages:
        text = text.replace(f"{percentage}%", f"{float(percentage):.0%}")
    return text


def loc(text):
    """Returns the localized string for the specified text.

    Parameters
    ----------
    text - the string to localize.

    Returns
    -------
    A localized to game.config.lang string.
    """
    lang = game_context.game.config.lang
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
            return loc(text[0]).format(*map(loc, text[1:]))
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
