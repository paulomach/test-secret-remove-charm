#!/usr/bin/env python3
# Copyright 2024 paulo
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following tutorial that will help you
develop a new k8s charm using the Operator Framework:

https://juju.is/docs/sdk/create-a-minimal-kubernetes-charm
"""

import logging

import ops
from ops.main import main

logger = logging.getLogger(__name__)

RELATION_A = "a-relation"
RELATION_B = "b-relation"


class RevokerCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.start, self.on_start)
        self.framework.observe(self.on[RELATION_A].relation_created, self.on_relation_created)
        self.framework.observe(self.on[RELATION_A].relation_broken, self.on_relation_broken_a)
        self.framework.observe(self.on[RELATION_B].relation_broken, self.on_relation_broken_b)
        self.framework.observe(self.on[RELATION_B].relation_changed, self.on_relation_changed)

    def on_start(self, _):
        self.unit.status = ops.model.ActiveStatus("Unit is ready")

    def on_relation_created(self, event):
        secret = self.model.app.add_secret(content={"dummy": "secret"})
        event.relation.data[self.app].update({"secret-id": secret.id})
        secret.grant(event.relation)
        self.unit.status = ops.model.ActiveStatus("Secret shared")

    def on_relation_broken_a(self, event):
        secret_id = event.relation.data[self.app].get("secret-id")
        secret = self.model.get_secret(id=secret_id)
        if self.config.get("remove-secret"):
            logger.info("Removing secret")
            secret.remove_all_revisions()
        else:
            logger.info("Skip secret removal")
        self.unit.status = ops.model.ActiveStatus("Unit is ready")

    def on_relation_broken_b(self, _):
        self.unit.status = ops.model.ActiveStatus("Unit is ready")

    def on_relation_changed(self, event):
        secret_id = event.relation.data[event.app].get("secret-id")
        secret = self.model.get_secret(id=secret_id)
        content = secret.peek_content()
        logger.info(f"Secret content: {content.get('dummy')}")
        self.unit.status = ops.model.ActiveStatus(f"Secret content: {content.get('dummy')}")


if __name__ == "__main__":
    main(RevokerCharm)
