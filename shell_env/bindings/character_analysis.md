

## Evolution of Bits to Characters and the Evolution of Unicode:
1. [ASCII table](http://www.asciitable.com/)
1. [Unicode includes ASCII](https://en.wikipedia.org/wiki/ASCII#Unicode)
1. and [Extends](http://www.unicode.org/charts/)


## BASIC TESTING
- `python -c "from curses import ascii as A; print A.unctrl(0x4A)"`
- `python -c "from curses import ascii as A; print A.unctrl(0x7d),A.unctrl(0x5B),A.ctrl(ord('C'));"`
- `xxd -pkg`
- `showkey -a`
- `tmux -C`

## COMMON KEYS/REPRESENTATIONS
| Key | Prefix-1 | Prefix-2 | Special Key Name
| :---| --- | --- | ---: |
| ctrl | 'C-' | '^'| |
| alt (meta) | 'M-' | | |


## OTHER SPECIALIZED / ADVANCED TOOLS

### INPUT ANALYSIS (Scancodes, Keycodes & associated decimal, hex, and binary formats)
- `im-config` - input method config framework
- `input-pad` - gtk-based virtual keyboard+ application
- `cutecom`/xenial 0.22.0-2 amd64  Graphical serial terminal, like minicom
- `kcharselect` - special character output to clipboard
- `node-ansi` - API for writing ANSI escape codes

### INPUT BINDING
- `dumpkeys`
- `xbindkeys` - bind keys to different key codes
- `xmodmap`
    - e.g., `xmodmap -e "keycode  71 = Hyper_L"`

### CHARACTER FORMATTING
- `bindechexascii`

### CHARACTER ENCODING (a.k.a. "CODEC") RECOGITION
- `uchardet` - C-based binding for universal charset detection library by Mozilla
- python[3]-chardet
- python[3]-libguess
- `tcs` - pan-pacific character set encoding
- `uniutils` - character encoding and font identification analysis
- `unifont`

### CHARACTER ENCODE/DECODE
- `iconv`
- `enca` (libenca-dev) - naive chardet analyzer
- `recode`

### CHARACTER TRANSLATION
- pypy-`unidecode` - ASCII transliterations of Unicode
- python[3]-unidecode
- golang-github-rainycape-unidecode-dev - ASCII transliterations of Unicode
- python-`translitcodec` - Unicode to 8-bit charset

### OTHER TOOLS
- `gnome-characters` - app for reviewing character map
- python[3]-shellescape - command line tool for maintaining persistent string handling across environments

* * *

1. establish/confirm scancodes
2. bind resulting keycodes to commands

## Example iTerm2 Scancode Bindings
| Hex         | In. ESC (Scancode) | Out ESC (Keycode) | GNU Str | Windows Str
|---          |---                 |---                |---      |---
| 02 1b 4f 43 | ^[OC               | [1;5C             | meta-OC | ctrl + shift + left
| 02 1b 4f 44 | ^[OD               | [1;5D             | meta-OD | ctrl + shift + right
| 02 1b 4f 41 | ^[OA               | [1;5A             | meta-OA | ctrl + shift + up
| 02 1b 4f 42 | ^[OB               | [1;5B             | meta-OB | ctrl + shift + down

## Example tmux Key Bindings

### context: WINDOW
| ACTION              | KEY              | BINDING | DESCRIPTION / [shell] MAPPING | CMD |
|:---                 |:---:             |:---      |:---          | |
| last-window         | S-C-a            | | | `bind -n S-C-a last-window`|
| previous-window     | S-Left           | | S arrow-left | `bind -n S-Left  previous-window`|
| next-window         | S-Right          | | S arrow-right | `bind -n S-Right next-window`|
| split-window -h     | M--              | M--      | Split pane|`bind -n M-<vertical bar> split-window -h`|
| split-window -v     | M-<vertical bar> | M-<vbar> ||`bind -n M-- split-window -v`|

## context: PANE
| ACTION              | KEY     | BINDING     | CMD                             |
|:---                 |:---:    |:---         |:---                             |
| resize-pane -L 5    |0x1b 0x68|C-M-S-left   |`bind -n M-h resize-pane -L 5`   |
| resize-pane -R 5    |0x1b 0x6C|C-M-S-right  |`bind -n M-l resize-pane -R 5`   |
| resize-pane -U 5    |0x1b 0x6A|C-M-S-up     |`bind -n M-j resize-pane -U 5`   |
| resize-pane -D 5    |0x1b 0x6B|C-M-S-down   |`bind -n M-k resize-pane -D 5`   |
| select-pane -L      |0x14 0xOE|C-M-left     |`bind -n M-Left select-pane -L`  |
| select-pane -R      |0x16 0x10|C-M-right    |`bind -n M-Right select-pane -R` |
| select-pane -U      |0x1b 0x6E|C-M-up       |`bind -n M-Up select-pane -U`    |
| select-pane -D      |0x1b 0x70|C-M-down     |`bind -n M-Down select-pane -D`  |

## context:
| ACTION              | KEY     | BINDING              | CMD|
|:---                 |:---:    |:---                  |:---|
|||||
|||||


### Notes
- tmux escape 0x02
- escape 0x1b ^[;
- delete 0x7f