import vedro.plugins.assert_rewriter
import vedro.plugins.director.rich
import vedro_d42_validator
import vedro_httpx
import vedro_pw


class Config(vedro.Config):

    class Plugins(vedro.Config.Plugins):

        class Playwright(vedro_pw.Playwright):
            enabled = True

        class VedroHTTPX(vedro_httpx.VedroHTTPX):
            enabled = True

        class D42Validator(vedro_d42_validator.D42Validator):
            enabled = True

        class RichReporter(vedro.plugins.director.rich.RichReporter):
            enabled = True
            show_paths = False
            show_scenario_spinner = True
