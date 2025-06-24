# 🌍 3D Earth Explorer

An interactive 3D Earth visualization built with Three.js that allows you to explore our planet with mouse controls.

## Features

- **Realistic Earth Rendering**: High-quality Earth textures with bump mapping and specular highlights
- **Cloud Layer**: Animated cloud cover that rotates independently
- **Atmospheric Glow**: Beautiful atmospheric effect around the Earth
- **Starfield Background**: Thousands of stars in the background for immersion
- **Interactive Controls**: 
  - Scroll to zoom in/out
  - Click and drag to rotate the Earth
  - Right-click and drag to pan
  - Auto-rotation for a dynamic view
- **Click Detection**: Click anywhere on Earth to see coordinates
- **Responsive Design**: Works on different screen sizes

## How to Use

1. **Open the Application**: Simply open `index.html` in a modern web browser
2. **Navigation**:
   - **Zoom**: Use your mouse wheel to zoom in and out
   - **Rotate**: Click and drag to rotate the Earth around
   - **Pan**: Right-click and drag to move the view
3. **Explore**: Click anywhere on the Earth to see the latitude and longitude coordinates
4. **Enjoy**: The Earth automatically rotates slowly for a dynamic experience

## Technical Details

- **Framework**: Three.js for 3D graphics
- **Textures**: High-resolution Earth textures from NASA
- **Controls**: OrbitControls for smooth camera manipulation
- **Performance**: Optimized for smooth 60fps rendering
- **Compatibility**: Works in all modern browsers with WebGL support

## File Structure

```
3DEarth/
├── index.html      # Main HTML file with styling
├── script.js       # JavaScript with Three.js implementation
└── README.md       # This file
```

## Browser Requirements

- Modern web browser with WebGL support
- Chrome, Firefox, Safari, or Edge (latest versions recommended)
- JavaScript enabled

## Customization

You can easily customize the Earth by modifying the `script.js` file:

- **Rotation Speed**: Change `controls.autoRotateSpeed`
- **Zoom Limits**: Adjust `controls.minDistance` and `controls.maxDistance`
- **Cloud Opacity**: Modify the `opacity` value in the clouds material
- **Star Count**: Change the loop count in `createStarfield()`

## Credits

- Earth textures from Three.js examples
- Built with Three.js library
- Inspired by space exploration and Earth visualization

Enjoy exploring our beautiful planet in 3D! 🌍✨ 