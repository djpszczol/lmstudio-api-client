# 🎨 Available Themes

LM Studio CLI Client uses Pygments for syntax highlighting. You can customize the theme by editing `~/.lmstudio-cli/config.json` and changing the `"theme"` value.

## Dark Themes

Popular dark themes for a comfortable viewing experience:

- **`monokai`** (default) - Classic dark theme with vibrant colors
- **`dracula`** - Popular modern dark theme
- **`one-dark`** - Atom's iconic dark theme
- **`gruvbox-dark`** - Retro groove dark theme
- **`github-dark`** - GitHub's dark mode theme
- **`nord`** - Arctic, north-bluish color palette
- **`nord-darker`** - Darker variant of Nord
- **`solarized-dark`** - Popular low-contrast dark theme
- **`material`** - Material Design inspired
- **`zenburn`** - Low-contrast dark theme
- **`paraiso-dark`** - Warm dark theme
- **`stata-dark`** - Statistical software inspired
- **`native`** - High contrast dark theme
- **`vim`** - Vim editor default colors
- **`fruity`** - Colorful dark theme
- **`inkpot`** - Deep purple dark theme

## Light Themes

Light themes for bright environments:

- **`default`** - Standard light theme
- **`friendly`** - Pleasant light theme
- **`colorful`** - Vibrant light theme
- **`gruvbox-light`** - Retro groove light variant
- **`solarized-light`** - Popular low-contrast light theme
- **`paraiso-light`** - Warm light theme
- **`stata-light`** - Light statistical theme
- **`autumn`** - Warm autumn colors
- **`emacs`** - Emacs editor default
- **`xcode`** - Apple's Xcode theme
- **`vs`** - Visual Studio theme
- **`tango`** - Tango Desktop Project colors
- **`pastie`** - Clean, minimal light theme
- **`perldoc`** - Perl documentation style
- **`borland`** - Classic Borland IDE colors
- **`manni`** - Soft, pleasant colors

## Specialty Themes

Unique or specialized themes:

- **`rainbow_dash`** - Extremely colorful theme
- **`arduino`** - Arduino IDE inspired
- **`coffee`** - Coffee-inspired warm tones
- **`algol`** - Classic programming language style
- **`igor`** - Scientific software inspired
- **`lightbulb`** - Bright and clear
- **`lilypond`** - Music notation inspired
- **`lovelace`** - Ada Lovelace tribute
- **`murphy`** - Murphy's theme
- **`rrt`** - Rudimentary theme
- **`staroffice`** - Office suite inspired
- **`trac`** - Trac project management

## How to Change Theme

1. Open the config file:
   ```bash
   nano ~/.lmstudio-cli/config.json
   ```

2. Change the `"theme"` value:
   ```json
   {
     "theme": "dracula"
   }
   ```

3. Save and restart the CLI

## Testing Themes

To preview a theme, you can temporarily change it and ask the AI to generate some code to see the syntax highlighting in action.

Example prompt:
```
Show me a Python function with loops and conditionals
```

Then use `/commands` to see the code highlighted with your chosen theme.
