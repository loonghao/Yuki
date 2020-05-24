# Import built-in modules
import sys

# Import third-party modules
from fbs_runtime.application_context.PySide2 import ApplicationContext

# Import local modules
from yuki import Controller
from yuki import View
from yuki import Model


class YuKiApplicationContext(ApplicationContext):

    def __init__(self):
        super(YuKiApplicationContext, self).__init__()
        self._gui = View()

    def show(self):
        model = Model(self)
        ctrl = Controller(model, self._gui, self)
        ctrl.show()
        exit_code = self.app.exec_()  # 2. Invoke appctxt.app.exec_()
        sys.exit(exit_code)


if __name__ == '__main__':
    app = YuKiApplicationContext()
    app.show()
