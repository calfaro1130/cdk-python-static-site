#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.infrastructure_stack import InfrastructureStack


app = cdk.App()
InfrastructureStack(app, "InfrastructureStack",)

app.synth()
