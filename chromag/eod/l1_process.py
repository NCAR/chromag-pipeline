# -*- coding: utf-8 -*-

from ..pipeline import step


@step()
def l1_process(run):
    run.logger.debug("L1 processing stuff...")
