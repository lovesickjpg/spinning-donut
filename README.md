# spinning-donut

ASCII donut spinning in the terminal. Python + numpy.

```
             $$$$$$$$$$$$$$$
          #$#####*******!!!****#
        ####****!!!!!!===!!!!=!!!!*
       **!!!!!!====;;::::~~~:::;;=====
      !!!!!!===;;:::~--,,,,,,---~~::;;;
      =====;;;:~~--,..........,--~::
      ;;;:;::~~-,......   .....,,-~~~
      ~:::~~~~--,,...-:=**$#*!=;:~~--,
        ---~-----~~:;=!*##$$##*!!=;:~,
           ..,---~~::;;===!!!!=;;~-,
                ...,,--~~~::::~-..
```

## run

```
pip install -r requirements.txt
python main.py
```

options:

- `--fps 60` – frame rate (default 30)
- `--speed 2` – rotation speed multiplier

Ctrl+C to quit. It adapts to the terminal size, resizing the window while it runs is fine.

## how it works

It's the classic [donut.c](https://www.a1k0n.net/2011/07/20/donut-math.html) by Andy Sloane:
take a circle, sweep it around an axis to get a torus, rotate it, project to 2D,
and pick a character based on how much the surface faces the light.

The first version of this repo did the projection with numpy but then went through
every point in a python loop for the z-buffer, which was slow. Now the z-buffer is
done with `np.maximum.at` too, so a frame takes ~1ms.

Also fixed along the way:

- the lighting formula was wrong, so the shading didn't really match the shape
- the donut was stretched vertically because terminal characters aren't square
- the cursor stayed hidden if the program crashed
