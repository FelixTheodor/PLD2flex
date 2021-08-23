import sys
from src.ContentManager import ContentManager

print("initializing...")
cm = ContentManager()
cm.init_process()
print("running...")
exit_code = cm.run()

print("stopped.")
sys.exit(exit_code)