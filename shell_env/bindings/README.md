

## Notes

- tmux escape { 'dec.':27,
				'hex':1B,
				'Oct':033 }

- tmux escape 0x02
- tmux escape 0x1b ^[;
- tmux delete 0x7f
- ;; ADJUST TAB [ M-A ... ]
- ;; ADJUST WINDOW [ C-M ... ]
- ;; ADJUST FRAME [ C-M-A ... ]

## Testing
- `python -c "from curses import ascii as A; print A.unctrl(0x4A)"`
- `python -c "from curses import ascii as A; print A.unctrl(0x7d),A.unctrl(0x5B),A.ctrl(ord('C'));"`
- `xxd -pkg`
- `showkey -a`
- `tmux -C`

##### [Other Resources](./character_analysis.md)

***

-------------------------------------------------------------------------------
## iTerm2
## tmux
## zsh

key: alt+x
cmd: helm

1. establish/confirm scancodes
2. bind resulting keycodes to commands

Key Code Result:

	Key Down
		Characters:	≈
		Unicode:		8776 / 0x2248
		Keys:		⌥X
		Key Code:	7 / 0x7
		Modifiers:	524576 / 0x80120

UNI_OUT_CFG="import sys; reload(sys); sys.setdefaultencoding('UTF8'); reload(sys)"
python -c "$UNI_OUT_CFG; print(unichr(8776))"
	--> ≈				(w/ UNICODE encoding)
	--> u'\u2248'		(w/ ASCII encoding)
python -c "$UNI_OUT_CFG; print(ord(u'\u2248'))"
	--> 8776


## COMMON KEYS/REPRESENTATIONS
| Key        | Prefix-1 | Prefix-2 |
| :---       | ---      | ---      |
| ctrl       | 'C-'     | '^'      |
| alt (meta) | 'M-'     |          |

## tmux Special Key Names (e.g., `send-keys -l Enter`; `send-keys "ls" Enter`):
- Up, Down, Left, Right
- Enter, Escape, Space, Tab, BTab (? confirmed ?)
- BSpace, BTab, IC (Insert), DC (Delete)
- F1 to F20
- Home, End
- NPage/PageDown/PgDn, PPage/PageUp/PgUp

send-keys 'M-X'

bind-key -n C-q new-session "monitor1" \; split-window -v "monitor2"



;;   | FRAME         | [ A-C-M-... ] |
;;   | TAB/WORKGROUP | [ M-A-... ]   |
;;   | WINDOW        | [ C-A-... ]   |
;;   | BUFFER        | [ C-b ... ]   |
;;   | TEXT          | [ A-c ... ]   |



## Example iTerm2 Scancode Bindings
| Hex         | In. ESC (Scancode) | Out ESC (Keycode) | GNU Str | Windows Str
|---          |---                 |---                |---      |---
| 02 1b 4f 43 | ^[OC               | [1;5C             | meta-OC | ctrl + shift + left
| 02 1b 4f 44 | ^[OD               | [1;5D             | meta-OD | ctrl + shift + right
| 02 1b 4f 41 | ^[OA               | [1;5A             | meta-OA | ctrl + shift + up
| 02 1b 4f 42 | ^[OB               | [1;5B             | meta-OB | ctrl + shift + down

## Example tmux Key Bindings

### context: WINDOW
| ACTION          | KEY              | BINDING  | DESCRIPTION / [shell] MAPPING | CMD                                        |
| :---            | :---:            | :---     | :---                          |                                            |
| last-window     | S-C-a            |          |                               | `bind -n S-C-a last-window`                |
| previous-window | S-Left           |          | S arrow-left                  | `bind -n S-Left  previous-window`          |
| next-window     | S-Right          |          | S arrow-right                 | `bind -n S-Right next-window`              |
| split-window -h | M--              | M--      | Split pane                    | `bind -n M-<vertical bar> split-window -h` |
| split-window -v | M-<vertical bar> | M-<vbar> |                               | `bind -n M-- split-window -v`              |

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
