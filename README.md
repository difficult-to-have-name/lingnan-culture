# Lingnan Culture Interactive Showcase

中文版见同目录下的 README_zh_hans.md

A Python application that showcases Lingnan culture through interactive visualizations using the `turtle` library. This project presents iconic elements of Lingnan culture—such as qilou (arcade houses), lion dance, and Cantonese language—with customizable features for an engaging user experience.


## Overview

Lingnan culture, rooted in southern China (covering present-day Guangdong, Guangxi, Hainan, Hong Kong, and Macau), is a rich blend of Cantonese, Chaoshan, and Hakka traditions. This application brings key cultural symbols to life through:
- **Interactive Qilou Visualization**: Draw and customize traditional arcade houses with adjustable columns and floors.
- **Lion Dance Showcase**: Display images and descriptions of the iconic southern lion dance.
- **Cantonese Language Features**: Highlight phrases and characteristics of the Cantonese dialect.


## Features

1. **Dynamic Qilou Drawing**  
   - Automatically generates traditional Lingnan-style arcade houses.  
   - Customization: Click the qilou to adjust the number of columns and floors via user input.  

2. **Cultural Elements Display**  
   - Lion dance imagery with detailed cultural descriptions.  
   - Cantonese phrases and linguistic explanations.  

3. **User-Friendly Interface**  
   - Intuitive click interactions for customization.  
   - Auto-scaling for Windows DPI settings to ensure display compatibility.  


## Technical Details

- **Programming Language**: Python 3.x  
- **Libraries**: `turtle` (for graphics), `base64` (for image handling), `tkinter` (for user dialogs).  
- **Modular Design**: Encapsulated classes for shapes (`BasicShape`), text display (`TextDisplayer`), image rendering (`ImageDisplayer`), and cultural elements (`Qilou`, `LionDance`, `Cantonese`).  


## How to Run

1. **Prerequisites**  
   Ensure Python 3.x is installed (32-bit or 64-bit). No additional dependencies are required beyond the standard library.

2. **Execution**  
   Run the main script directly:  
   ```bash
   python main.py
   ```

3. **Customization**  
   - Click the qilou structure to open input prompts for adjusting columns and floors.  
   - Follow on-screen instructions (in Chinese) for interactive features.  


## Packaging

To generate standalone executables for Windows:

1. Install `pyinstaller`:  
   ```bash
   pip install pyinstaller
   ```

2. Use the provided `app.spec` file to build:  
   ```bash
   # For 64-bit systems
   pyinstaller app.spec --distpath dist_x64

   # For 32-bit systems (run in a 32-bit Python environment)
   pyinstaller app.spec --distpath dist_x86 --platform=win32
   ```

3. The executable `LingnanCulture.exe` will be generated in the specified `dist` directory.


## License

This project is licensed under the Apache License 2.0. See the [LICENSE](http://www.apache.org/licenses/LICENSE-2.0) file for details.


## Acknowledgments

- Designed for the Informatics Innovation Competition AI Algorithm Challenge.  
- Celebrating Lingnan culture's heritage and diversity through technology.