Once you've dragged the Figure-Tek folder into your `Maya/scripts` folder, you should be able to access commands located within the package.

To select all animation controls and zero them to the bind pose, run this in a Python script editor:

```python
import FT_public.FT_utils as FT_utils
FT_utils.select_all()
FT_utils.set_bindpose()
