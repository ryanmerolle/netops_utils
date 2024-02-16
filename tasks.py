from invoke import task


@task
def ruff(ctx):
    ctx.run("ruff .")


@task
def ruff_format(ctx):
    ctx.run("ruff format .")


@task
def install_app(ctx):
    ctx.run("pip install -e .")


@task
def update_poetry(ctx):
    ctx.run("poetry update")


@task
def run_megalinter(ctx):
    ctx.run("docker run -v $(pwd):/tmp/lint nvuillam/mega-linter")


@task
def black(ctx):
    ctx.run("black .")


@task
def megalinter(ctx):
    ctx.run("docker run -v $(pwd):/tmp/lint nvuillam/mega-linter")
