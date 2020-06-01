# BitHunter

BitHunter is a tool to pull trophy images and apply custom frames to them.
The tool can be configured to export to multiple sizes and multiple formats.

## How to use

When you run BitHunter, you have two options, adding frames to local images (typing `0`), or pulling the images from the web.

If you want to apply a custom frame to the images, create one called `frame.png` and place it inside the root folder.

### Pulling from the web

BitHunter will ask you to type a GameID. This can be found in the game page as part of the game's URL

`https://psnprofiles.com/trophies/GameID-game-name`

After pressing Enter, BitHunter will start pulling all the images and resizing them. The framed images will be stored in `/processed`. If you have set yout configuration file with `storeOriginals` set to `true`, the original non-framed images will be stored in `/originals`.

### Processing local images

If you already have some trophy images stored locally, and you want to just apply the frame to them, place all of them in the `/consume` folder. Then start BitHunter and press `0`. Make sure the frame thickness is configured correctly in the configuration file.

## Config file

In the root folder you will find a `config.json` file. You can edit it to customize your settings.

| Var            | Description                                                       | Accepted values |
| -------------- | ----------------------------------------------------------------- | --------------- |
| storeOriginals | If you want to store the original images without frame            | `true`/`false`  |
| acceptedTypes  | File types accepted                                               | `string`        |
| frameThickness | How thick is `frame.png` (in pixels)                              | `int`           |
| exportSizes    | Sizes you wish to export to (accepts multiple)                    | `int`           |
| exportTypes    | File types you wish to export to (accepts multiple)               | `string`        |
| imageNameRoot  | Text before filename. Accepts `@g`/`@t`/`@s` for game/trophy/size | `string`        |
| imageNameEnd   | Text after filename. Accepts `@g`/`@t`/`@s` for game/trophy/size  | `string`        |

_Example 1:_

```
    "storeOriginals": false,
    "acceptedTypes": [".PNG", ".JPG", ".JPEG"],
    "frameWidth": 15,
    "exportSizes": [240, 120],
    "exportTypes": [".JPEG", ".PNG"]
    "imageNameRoot": 'bit-@t',
    "imageNameEnd": '@s'
```

BitHunter will load the trophy images without storing them on your drive, and will then apply a 15pixel thick frame to them. It will export 240x240 and 120x120 images both in .jpeg and .png format. The file name will be `bit-trophyName-XXXXXXX-imageSize.fileType`

_Example 2:_

```
    "storeOriginals": true,
    "acceptedTypes": [".PNG", ".JPG", ".JPEG"],
    "frameWidth": 20,
    "exportSizes": [64],
    "exportTypes": [".PNG"]
    "imageNameRoot": '@g-wow-@s',
    "imageNameEnd": '@t'
```

BitHunter will load the trophy images and store them in the `/originals` folder. Then it will apply a 20px thick frame, and export 64x64 images both in .png format. . The file name will be `gameName-wow-imageSize-XXXXXXX-trophyName.fileType`

_Example 3:_

```
    "storeOriginals": true,
    "acceptedTypes": [".PNG", ".JPG", ".JPEG"],
    "frameWidth": 4,
    "exportSizes": [128, 64, 32],
    "exportTypes": [".PNG"]
    "imageNameRoot": ''
    "imageNameEnd": ''
```

BitHunter will load the trophy images and store them in the `/originals` folder. Then it will apply a 4px thick frame, and export 128x128, 64x64 and 32x32 images both in .png format. . The file name will be `XXXXXXX.fileType`
