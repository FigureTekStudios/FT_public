
##  **Installing FT_public**
Drag the Figure-Tek folder (at the same level as this readme.md) to  your `Maya/scripts` folder

##  Reset animation controls
To select all animation controls and zero them to the bind pose, run this in a Python script editor:

```python
import FT_public.FT_utils as FT_utils
FT_utils.select_all()
FT_utils.set_bindpose()
```

## Steps to Import Accessories

1. **Download and Unzip**: Download and unzip the accessory folder (e.g., `Handwraps_GJ5-DD3-DCH2`).
2. **Create Directory**: Create a location on your drive to house the accessory folder and any other accessories you might want to purchase.
3. **Install FT_public**: Ensure you have the latest Figure-Tek tools package (`FT_public`) installed in your Maya scripts directory.
4. **Run Script**: In a Maya Python script editor, run the above commands to load the accessory folders.


Import accessories with the following commands:
```
from FT_public import FT_accessories
FT_accessories.load_accessory_folders()
```


Load the model OBJs.
Organize them.
Skin them to the rig.
Bring in material networks.
Copy any texture files neatly into your character's source image folder.
