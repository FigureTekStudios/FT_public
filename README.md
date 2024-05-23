
##  **Installing FT_public**
Drag the Figure-Tek folder (at the same level as this readme.md) to  your `Maya/scripts` folder


## Animation commands
###  Reset animation controls
To select all animation controls and zero them to the bind pose, run this in a Python script editor:

```python
import FT_public.FT_utils as FT_utils
FT_utils.select_all()
FT_utils.set_bindpose()
```

## Steps to Import Figure-Tek Accessories
1. **Install FT_public**: Ensure you have the latest Figure-Tek tools package (`FT_public`) installed in your Maya scripts directory.
2.  **Create an accessories directory**: Create a folder named accessories or FT_accessories on your documents folder or somewhere on your drive. 
3. **Download and Unzip**: Download your asset from Gumroad. Ill use https://figuretek.gumroad.com/l/GJ5-DD3-DCH2 as an example asset. Unzip it and youll end up with what  an
      accessory folder named Handwraps_GJ5-DD3-DCH2. The first part of the name is the asset name, and the second is the FT_ID which every asset has.



4. **Run Script**: In a Maya Python script editor, run the above commands to load the accessory folders.


get FT_public recopied to your maya scripts folder
 open the rig (PG4_REF.ma)  set your project if you havent already.

run this in a maya python script editor:

from FT_public import FT_accessories
FT_accessories.load_accessory_folders() (edited)


Import accessories with the following commands:
```
from FT_public import FT_accessories
FT_accessories.load_accessory_folders()
```

  thatll load all the outfit pieces up for you, skin them, and hook up the textures. itll also copy the textrure from your asset library over to the character folder so the character is all still   self containted. 

