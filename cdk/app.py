#!/usr/bin/env python3

import os

from aws_cdk import App

from playground.fargate_stack import FargateStack
from playground.playground_stack import PlaygroundStack

app = App()
PlaygroundStack(app, "playground")
FargateStack(app, "fargate")

app.synth()
