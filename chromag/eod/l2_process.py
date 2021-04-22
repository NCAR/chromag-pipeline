# -*- coding: utf-8 -*-

from ..pipeline import step


@step()
def l2_process(run):
    run.logger.debug("L2 processing stuff...")
