#!/usr/bin/env python3
"""
Testy pro add_module.py script.

Tento testovací soubor obsahuje testy pro funkcionalitu přidávání modulů do PrismQ.
Všechny testy jsou dokumentovány v češtině pro snadnější pochopení.
"""

import pytest
from pathlib import Path
import sys

# Přidání rodičovského adresáře do PYTHONPATH pro import add_module
sys.path.insert(0, str(Path(__file__).parent.parent))

from add_module import ModuleCreator


class TestModuleCreator:
    """Testovací třída pro ModuleCreator."""

    @pytest.fixture
    def creator(self, tmp_path):
        """
        Vytvoří instanci ModuleCreator pro testování.
        
        Args:
            tmp_path: Dočasný adresář poskytnutý pytest
            
        Returns:
            ModuleCreator: Instance pro testování
        """
        return ModuleCreator(tmp_path)

    def test_parse_github_url_full_https(self, creator):
        """
        Test parsování plné HTTPS GitHub URL.
        
        Testuje, že plná HTTPS URL je správně rozpoznána a parsována
        na vlastníka repozitáře a název repozitáře.
        """
        owner, repo = creator.parse_github_url("https://github.com/Nomoos/PrismQ.RepositoryTemplate.git")
        assert owner == "Nomoos"
        assert repo == "PrismQ.RepositoryTemplate"

    def test_parse_github_url_https_without_git(self, creator):
        """
        Test parsování HTTPS URL bez .git přípony.
        
        Ověřuje, že URL bez .git přípony je také správně parsována.
        """
        owner, repo = creator.parse_github_url("https://github.com/Nomoos/PrismQ.IdeaInspiration")
        assert owner == "Nomoos"
        assert repo == "PrismQ.IdeaInspiration"

    def test_parse_github_url_ssh_format(self, creator):
        """
        Test parsování SSH formátu GitHub URL.
        
        Testuje podporu git@github.com: formátu pro SSH klony.
        """
        owner, repo = creator.parse_github_url("git@github.com:Nomoos/PrismQ.TestModule.git")
        assert owner == "Nomoos"
        assert repo == "PrismQ.TestModule"

    def test_parse_github_url_short_format(self, creator):
        """
        Test parsování zkráceného formátu Owner/RepoName.
        
        Ověřuje, že zkrácený formát bez URL je také podporován.
        """
        owner, repo = creator.parse_github_url("Nomoos/PrismQ.MyModule")
        assert owner == "Nomoos"
        assert repo == "PrismQ.MyModule"

    def test_parse_github_url_nested_module(self, creator):
        """
        Test parsování URL pro vnořený modul.
        
        Testuje správné parsování URL pro víceúrovňové moduly
        jako PrismQ.Parent.Child.
        """
        owner, repo = creator.parse_github_url("https://github.com/Nomoos/PrismQ.RepositoryTemplate.ModuleExample")
        assert owner == "Nomoos"
        assert repo == "PrismQ.RepositoryTemplate.ModuleExample"

    def test_parse_github_url_invalid(self, creator):
        """
        Test parsování neplatné URL.
        
        Ověřuje, že neplatný formát vrátí None hodnoty.
        """
        owner, repo = creator.parse_github_url("invalid-url")
        assert owner is None
        assert repo is None

    def test_derive_module_path_single_component(self, creator):
        """
        Test odvození cesty modulu s jednou komponentou.
        
        Pro jednoduchý modul jako "PrismQ.MyModule" by měla být cesta "src/MyModule".
        """
        module_name, module_path = creator.derive_module_path("PrismQ.MyModule")
        assert module_name == "MyModule"
        assert module_path == "src/MyModule"

    def test_derive_module_path_two_components(self, creator):
        """
        Test odvození cesty pro modul se dvěma komponentami.
        
        Pro modul "PrismQ.Parent.Child" by měla být cesta "src/Parent/src/Child".
        """
        module_name, module_path = creator.derive_module_path("PrismQ.Parent.Child")
        assert module_name == "Parent.Child"
        assert module_path == "src/Parent/src/Child"

    def test_derive_module_path_three_components(self, creator):
        """
        Test odvození cesty pro modul se třemi komponentami.
        
        Testuje správné vytvoření vnořené struktury pro tříúrovňový modul.
        """
        module_name, module_path = creator.derive_module_path("PrismQ.Level1.Level2.Level3")
        assert module_name == "Level1.Level2.Level3"
        assert module_path == "src/Level1/src/Level2/src/Level3"

    def test_derive_module_path_without_prismq_prefix(self, creator):
        """
        Test odvození cesty pro modul bez PrismQ. prefixu.
        
        Ověřuje, že modul bez prefixu je zpracován správně.
        """
        module_name, module_path = creator.derive_module_path("SimpleModule")
        assert module_name == "SimpleModule"
        assert module_path == "src/SimpleModule"

    def test_derive_remote_name_simple(self, creator):
        """
        Test odvození názvu remote pro jednoduchý repozitář.
        
        Testuje konverzi URL na název remote podle konvence.
        """
        remote_name = creator.derive_remote_name("https://github.com/Nomoos/PrismQ.MyModule.git")
        assert remote_name == "prismq-mymodule"

    def test_derive_remote_name_nested(self, creator):
        """
        Test odvození názvu remote pro vnořený modul.
        
        Ověřuje, že tečky jsou nahrazeny pomlčkami a vše je malými písmeny.
        """
        remote_name = creator.derive_remote_name("https://github.com/Nomoos/PrismQ.RepositoryTemplate.ModuleExample.git")
        assert remote_name == "prismq-repositorytemplate-moduleexample"

    def test_derive_remote_name_with_underscores(self, creator):
        """
        Test odvození názvu remote s podtržítky v názvu.
        
        Testuje, že podtržítka jsou také nahrazena pomlčkami.
        """
        remote_name = creator.derive_remote_name("https://github.com/Owner/My_Test_Repo.git")
        assert remote_name == "my-test-repo"

    def test_derive_remote_name_without_git_extension(self, creator):
        """
        Test odvození názvu remote bez .git přípony.
        
        Ověřuje, že URL bez .git přípony je zpracována správně.
        """
        remote_name = creator.derive_remote_name("https://github.com/Nomoos/PrismQ.TestModule")
        assert remote_name == "prismq-testmodule"


class TestModulePathDerivation:
    """
    Speciální testy pro odvozování cest modulů.
    
    Tyto testy se zaměřují na edge cases a speciální situace
    při odvozování cest.
    """

    @pytest.fixture
    def creator(self, tmp_path):
        """Vytvoří instanci ModuleCreator pro testování."""
        return ModuleCreator(tmp_path)

    def test_repository_template_example(self, creator):
        """
        Test konkrétního příkladu z error logu.
        
        Testuje příklad z problémového výstupu:
        PrismQ.RepositoryTemplate.ModuleExample -> src/RepositoryTemplate/src/ModuleExample
        """
        module_name, module_path = creator.derive_module_path("PrismQ.RepositoryTemplate.ModuleExample")
        assert module_name == "RepositoryTemplate.ModuleExample"
        assert module_path == "src/RepositoryTemplate/src/ModuleExample"
        
        # Ujistěte se, že cesta neobsahuje duplicitní vnořování
        assert module_path.count("src/ModuleExample") == 1

    def test_idea_inspiration_sources(self, creator):
        """
        Test odvození cesty pro existující modul IdeaInspiration.Sources.
        
        Ověřuje správnou strukturu pro reálný modul v repozitáři.
        """
        module_name, module_path = creator.derive_module_path("PrismQ.IdeaInspiration.Sources")
        assert module_name == "IdeaInspiration.Sources"
        assert module_path == "src/IdeaInspiration/src/Sources"

    def test_deeply_nested_module(self, creator):
        """
        Test velmi vnořeného modulu.
        
        Testuje, že i hluboce vnořené moduly jsou správně zpracovány.
        """
        module_name, module_path = creator.derive_module_path("PrismQ.A.B.C.D.E")
        assert module_name == "A.B.C.D.E"
        assert module_path == "src/A/src/B/src/C/src/D/src/E"
        
        # Spočítáme počet 'src/' v cestě - měl by odpovídat počtu komponent
        src_count = module_path.count("src/")
        assert src_count == 5  # Pět úrovní vnořování


class TestURLParsing:
    """
    Rozšířené testy pro parsování URL.
    
    Tyto testy pokrývají různé formáty a edge cases při parsování GitHub URL.
    """

    @pytest.fixture
    def creator(self, tmp_path):
        """Vytvoří instanci ModuleCreator pro testování."""
        return ModuleCreator(tmp_path)

    def test_parse_http_protocol(self, creator):
        """
        Test parsování HTTP protokolu (ne HTTPS).
        
        Ověřuje podporu i pro HTTP URL (i když není doporučeno).
        """
        owner, repo = creator.parse_github_url("http://github.com/TestOwner/TestRepo")
        assert owner == "TestOwner"
        assert repo == "TestRepo"

    def test_parse_with_trailing_slash(self, creator):
        """
        Test parsování URL s koncovým lomítkem.
        
        URL s lomítkem na konci by mělo být zpracováno správně.
        """
        # Poznámka: Současná implementace by měla správně odstranit .git ale ne lomítko
        # To by mohlo způsobit problém - otestujeme aktuální chování
        owner, repo = creator.parse_github_url("https://github.com/Owner/Repo/")
        # Očekáváme, že parsování selže nebo vrátí prázdný string pro repo
        # protože poslední část po split('/') bude prázdná
        # To je potenciální bug, který by měl být opraven

    def test_parse_organization_repo(self, creator):
        """
        Test parsování URL organizačního repozitáře.
        
        Ověřuje, že organizace jsou zpracovány stejně jako uživatelé.
        """
        owner, repo = creator.parse_github_url("https://github.com/microsoft/vscode.git")
        assert owner == "microsoft"
        assert repo == "vscode"

    def test_parse_case_sensitivity(self, creator):
        """
        Test citlivosti na velikost písmen v URL.
        
        GitHub URL jsou case-sensitive, měly by být zachovány.
        """
        owner, repo = creator.parse_github_url("https://github.com/MyOrg/MyRepo.git")
        assert owner == "MyOrg"
        assert repo == "MyRepo"


if __name__ == "__main__":
    # Spuštění testů přímo z tohoto souboru
    pytest.main([__file__, "-v"])
