Once youve dragged the Figure-Tek folder into the your Maya/scripts folder you should be able to access commands located within the package.

To select all animation controls and zero them to the bind pose, run this in a python script editor.

import FT_public.FT_utils as FT_utils
FT_utils.select_all()
FT_utils.set_bindpose()

You can also highlight and drag the code from the script editor up to your shelf. The bindpose command works with whatever is selected.
