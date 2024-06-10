
##  **Installing FT_public**
Press the green <> Code button and download the zipped up code. Unzip. Within the new folder named FT_public-main youll find FT_public. Drag the Figure-Tek folder (at the same directory level as this readme.md) to  your `Documents/Maya/scripts` folder
It should look like this image:
![image](https://github.com/FigureTekStudios/FT_public/assets/9369366/d34fd0f7-5b58-4b3a-9ea7-d71f2844af6b)


## Animation commands
###  Reset animation controls
To select all animation controls and zero them to the bind pose, run this in a Python script editor:

```python
import FT_public.FT_utils as FT_utils
FT_utils.select_all()
FT_utils.set_bindpose()
```

## Steps to Import Figure-Tek Accessories
1. **Ensure you have the latest Figure-Tek tools package** `FT_public` installed in your Maya scripts directory.

2.  **Create an accessories directory**: Create a folder named `accessories` in your documents folder or somewhere on your drive. 

3. **Download and Unzip**: Download your asset from Gumroad. Ill use the Handwraps asset, https://figuretek.gumroad.com/l/GJ5-DD3-DCH2 as an example asset. Unzip it and you'll end up with an accessory folder named FT_Handwraps_GJ5-DD3-DCH2.

4. **Make sure you set your project to your characters folder** I'll use FT_human_female_PG4-HJ8-GHF5', the flagship character as an example. The charachers folder is named `FT_human_female_PG4-HJ8-GHF5`. Setting the project is important so the script will know where to copy texture maps to your characters _rig directory. 

5. **Open up your Figure-Tek charachter rig scene**: Her rig file is located wherever you stored the asset then ..\FT_HumanFemale_PG4-HJ8-GHF5\_rig\PG4.mb
      
4. **Run Script**: In a Maya Python script editor, run the following commands:
      ```
      from FT_public import FT_accessories
      FT_accessories.load_accessory_folders()
      ```
5. **Select the asset folder**: Navigate to your `accessories` folder where youve stored your accessory asset folders, in our example 
FT_Handwraps_GJ5-DD3-DCH2 and press choose.   That'll load all the outfit pieces up for you, skin them, and hook up the textures. It'll also copy the texture from your asset library over to the character folder so the character project is all still self contained. 

