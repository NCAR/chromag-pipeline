# -*- coding: utf-8 -*-

from ..pipeline import step


@step()
def inventory(run):
    run.logger.debug("doing inventory stuff...")
 
