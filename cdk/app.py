#!/usr/bin/env python3

import os

from aws_cdk import App

from playground.playground_stack import PlaygroundStack

app = App()
PlaygroundStack(app, "playground")

app.synth()
