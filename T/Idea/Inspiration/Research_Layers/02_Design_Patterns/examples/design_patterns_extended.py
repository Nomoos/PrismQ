#!/usr/bin/env python3
"""
Rozšířené Design Patterns pro PrismQ.IdeaInspiration

Tento soubor demonstruje další design patterns kromě základních pěti:
1. Decorator Pattern - Dynamické přidání funkcionalit
2. Chain of Responsibility - Řetězec zpracovatelů
3. Command Pattern - Zapouzdření požadavků
4. State Pattern - Změna chování podle stavu
5. Composite Pattern - Hierarchická struktura objektů
6. Proxy Pattern - Kontrola přístupu
7. Builder Pattern - Krok za krokem konstrukce objektů
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Protocol

# =============================================================================
# 1. DECORATOR PATTERN - Dynamické Přidání Funkcionalit
# =============================================================================


@dataclass
class Video:
    """Video data model."""

    id: str
    title: str
    url: str


class VideoFetcher(Protocol):
    """Protokol pro získání videí."""

    def fetch(self, url: str) -> Video:
        """Získat video z URL."""
        ...


class BasicVideoFetcher:
    """Základní implementace získání videa."""

    def fetch(self, url: str) -> Video:
        """Získat video bez cachování či logování."""
        print(f"[BasicFetcher] Získávám video z {url}")
        return Video(id="1", title="Video", url=url)


class LoggingVideoFetcher:
    """Decorator přidávající logování."""

    def __init__(self, fetcher: VideoFetcher):
        self._fetcher = fetcher

    def fetch(self, url: str) -> Video:
        """Získat video s logováním."""
        print(f"[LoggingDecorator] Začínám získávat: {url}")
        video = self._fetcher.fetch(url)
        print(f"[LoggingDecorator] Dokončeno: {video.title}")
        return video


class CachingVideoFetcher:
    """Decorator přidávající cachování."""

    def __init__(self, fetcher: VideoFetcher):
        self._fetcher = fetcher
        self._cache: Dict[str, Video] = {}

    def fetch(self, url: str) -> Video:
        """Získat video s cachováním."""
        if url in self._cache:
            print(f"[CachingDecorator] Vráceno z cache: {url}")
            return self._cache[url]

        video = self._fetcher.fetch(url)
        self._cache[url] = video
        return video


class RetryVideoFetcher:
    """Decorator přidávající retry logiku."""

    def __init__(self, fetcher: VideoFetcher, max_retries: int = 3):
        self._fetcher = fetcher
        self._max_retries = max_retries

    def fetch(self, url: str) -> Video:
        """Získat video s retry."""
        for attempt in range(self._max_retries):
            try:
                print(f"[RetryDecorator] Pokus {attempt + 1}/{self._max_retries}")
                return self._fetcher.fetch(url)
            except Exception as e:
                if attempt == self._max_retries - 1:
                    raise
                print(f"[RetryDecorator] Chyba: {e}, zkouším znovu...")
        raise Exception("Max retries exceeded")


# =============================================================================
# 2. CHAIN OF RESPONSIBILITY - Řetězec Zpracovatelů
# =============================================================================


@dataclass
class Request:
    """Požadavek na zpracování."""

    content: str
    priority: int


class Handler(ABC):
    """Abstraktní handler v řetězci."""

    def __init__(self):
        self._next_handler: Optional[Handler] = None

    def set_next(self, handler: "Handler") -> "Handler":
        """Nastavit další handler v řetězci."""
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: Request) -> Optional[str]:
        """Zpracovat požadavek."""
        pass

    def _pass_to_next(self, request: Request) -> Optional[str]:
        """Předat požadavek dalšímu handleru."""
        if self._next_handler:
            return self._next_handler.handle(request)
        return None


class SpamFilterHandler(Handler):
    """Handler pro filtrování spamu."""

    def handle(self, request: Request) -> Optional[str]:
        """Filtrovat spam."""
        if "spam" in request.content.lower():
            print(f"[SpamFilter] Zablokován spam: {request.content}")
            return "BLOCKED"
        return self._pass_to_next(request)


class PriorityHandler(Handler):
    """Handler pro zpracování priority."""

    def handle(self, request: Request) -> Optional[str]:
        """Zpracovat podle priority."""
        if request.priority >= 5:
            print(f"[PriorityHandler] Vysoká priorita: {request.priority}")
            # Zpracovat okamžitě
            return "HIGH_PRIORITY_PROCESSED"
        return self._pass_to_next(request)


class ContentHandler(Handler):
    """Handler pro zpracování obsahu."""

    def handle(self, request: Request) -> Optional[str]:
        """Zpracovat obsah."""
        print(f"[ContentHandler] Zpracovávám: {request.content}")
        return "PROCESSED"


# =============================================================================
# 3. COMMAND PATTERN - Zapouzdření Požadavků
# =============================================================================


class Command(ABC):
    """Abstraktní command."""

    @abstractmethod
    def execute(self) -> None:
        """Provést příkaz."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Vrátit zpět příkaz."""
        pass


@dataclass
class IdeaInspiration:
    """Doménový model."""

    id: str
    title: str
    status: str = "draft"


class IdeaRepository:
    """Repository pro ideas."""

    def __init__(self):
        self._ideas: Dict[str, IdeaInspiration] = {}

    def save(self, idea: IdeaInspiration) -> None:
        """Uložit idea."""
        self._ideas[idea.id] = idea
        print(f"[Repository] Uloženo: {idea.title}")

    def remove(self, idea_id: str) -> Optional[IdeaInspiration]:
        """Odstranit idea."""
        idea = self._ideas.pop(idea_id, None)
        if idea:
            print(f"[Repository] Odstraněno: {idea.title}")
        return idea

    def get(self, idea_id: str) -> Optional[IdeaInspiration]:
        """Získat idea."""
        return self._ideas.get(idea_id)


class CreateIdeaCommand(Command):
    """Příkaz pro vytvoření idea."""

    def __init__(self, repository: IdeaRepository, idea: IdeaInspiration):
        self._repository = repository
        self._idea = idea

    def execute(self) -> None:
        """Vytvořit idea."""
        print(f"[Command] Vytvářím idea: {self._idea.title}")
        self._repository.save(self._idea)

    def undo(self) -> None:
        """Vrátit zpět vytvoření."""
        print(f"[Command] Vracím zpět vytvoření: {self._idea.title}")
        self._repository.remove(self._idea.id)


class PublishIdeaCommand(Command):
    """Příkaz pro publikování idea."""

    def __init__(self, repository: IdeaRepository, idea_id: str):
        self._repository = repository
        self._idea_id = idea_id
        self._previous_status = None

    def execute(self) -> None:
        """Publikovat idea."""
        idea = self._repository.get(self._idea_id)
        if idea:
            self._previous_status = idea.status
            idea.status = "published"
            print(f"[Command] Publikuji: {idea.title}")

    def undo(self) -> None:
        """Vrátit zpět publikování."""
        idea = self._repository.get(self._idea_id)
        if idea and self._previous_status:
            idea.status = self._previous_status
            print(f"[Command] Vracím zpět publikování: {idea.title}")


class CommandInvoker:
    """Invoker pro provádění příkazů."""

    def __init__(self):
        self._history: List[Command] = []

    def execute(self, command: Command) -> None:
        """Provést příkaz a uložit do historie."""
        command.execute()
        self._history.append(command)

    def undo(self) -> None:
        """Vrátit zpět poslední příkaz."""
        if self._history:
            command = self._history.pop()
            command.undo()
        else:
            print("[Invoker] Žádné příkazy k vrácení")


# =============================================================================
# 4. STATE PATTERN - Změna Chování podle Stavu
# =============================================================================


class WorkerState(ABC):
    """Abstraktní stav workera."""

    @abstractmethod
    def start_task(self, worker: "Worker") -> None:
        """Začít úkol."""
        pass

    @abstractmethod
    def complete_task(self, worker: "Worker") -> None:
        """Dokončit úkol."""
        pass

    @abstractmethod
    def fail_task(self, worker: "Worker") -> None:
        """Selhání úkolu."""
        pass


class IdleState(WorkerState):
    """Stav nečinnosti."""

    def start_task(self, worker: "Worker") -> None:
        """Začít úkol z nečinnosti."""
        print("[IdleState] Začínám úkol...")
        worker.set_state(ProcessingState())

    def complete_task(self, worker: "Worker") -> None:
        """Nelze dokončit úkol v nečinnosti."""
        print("[IdleState] Nelze dokončit - nejsou žádné úkoly")

    def fail_task(self, worker: "Worker") -> None:
        """Nelze selhat v nečinnosti."""
        print("[IdleState] Nelze selhat - nejsou žádné úkoly")


class ProcessingState(WorkerState):
    """Stav zpracování."""

    def start_task(self, worker: "Worker") -> None:
        """Nelze začít další úkol během zpracování."""
        print("[ProcessingState] Již zpracovávám úkol")

    def complete_task(self, worker: "Worker") -> None:
        """Dokončit úkol."""
        print("[ProcessingState] Dokončuji úkol...")
        worker.set_state(IdleState())

    def fail_task(self, worker: "Worker") -> None:
        """Úkol selhal."""
        print("[ProcessingState] Úkol selhal...")
        worker.set_state(ErrorState())


class ErrorState(WorkerState):
    """Stav chyby."""

    def start_task(self, worker: "Worker") -> None:
        """Restart po chybě."""
        print("[ErrorState] Restartování a začínám nový úkol...")
        worker.set_state(ProcessingState())

    def complete_task(self, worker: "Worker") -> None:
        """Nelze dokončit v error stavu."""
        print("[ErrorState] Nelze dokončit - worker má chybu")

    def fail_task(self, worker: "Worker") -> None:
        """Již v error stavu."""
        print("[ErrorState] Již v error stavu")


class Worker:
    """Worker se stavem."""

    def __init__(self):
        self._state: WorkerState = IdleState()
        print("[Worker] Inicializován v Idle stavu")

    def set_state(self, state: WorkerState) -> None:
        """Nastavit nový stav."""
        self._state = state

    def start_task(self) -> None:
        """Začít úkol."""
        self._state.start_task(self)

    def complete_task(self) -> None:
        """Dokončit úkol."""
        self._state.complete_task(self)

    def fail_task(self) -> None:
        """Selhání úkolu."""
        self._state.fail_task(self)


# =============================================================================
# 5. BUILDER PATTERN - Krok za Krokem Konstrukce
# =============================================================================


@dataclass
class VideoTask:
    """Komplexní video úkol."""

    video_id: str
    title: Optional[str] = None
    priority: int = 5
    retry_count: int = 3
    timeout: int = 30
    metadata: Optional[Dict[str, Any]] = None
    callbacks: Optional[List[Callable]] = None


class VideoTaskBuilder:
    """Builder pro vytvoření video úkolu."""

    def __init__(self, video_id: str):
        self._video_id = video_id
        self._title: Optional[str] = None
        self._priority: int = 5
        self._retry_count: int = 3
        self._timeout: int = 30
        self._metadata: Dict[str, Any] = {}
        self._callbacks: List[Callable] = []

    def with_title(self, title: str) -> "VideoTaskBuilder":
        """Nastavit titulek."""
        self._title = title
        return self

    def with_priority(self, priority: int) -> "VideoTaskBuilder":
        """Nastavit prioritu."""
        self._priority = priority
        return self

    def with_retry_count(self, count: int) -> "VideoTaskBuilder":
        """Nastavit počet opakování."""
        self._retry_count = count
        return self

    def with_timeout(self, timeout: int) -> "VideoTaskBuilder":
        """Nastavit timeout."""
        self._timeout = timeout
        return self

    def add_metadata(self, key: str, value: Any) -> "VideoTaskBuilder":
        """Přidat metadata."""
        self._metadata[key] = value
        return self

    def add_callback(self, callback: Callable) -> "VideoTaskBuilder":
        """Přidat callback."""
        self._callbacks.append(callback)
        return self

    def build(self) -> VideoTask:
        """Vytvořit úkol."""
        return VideoTask(
            video_id=self._video_id,
            title=self._title,
            priority=self._priority,
            retry_count=self._retry_count,
            timeout=self._timeout,
            metadata=self._metadata if self._metadata else None,
            callbacks=self._callbacks if self._callbacks else None,
        )


# =============================================================================
# DEMONSTRACE
# =============================================================================


def demonstrate_decorator():
    """Demonstrace Decorator Pattern."""
    print("\n" + "=" * 70)
    print("1. DECORATOR PATTERN - Dynamické Přidání Funkcionalit")
    print("=" * 70)

    # Základní fetcher
    fetcher = BasicVideoFetcher()

    # Přidání cachování
    fetcher = CachingVideoFetcher(fetcher)

    # Přidání logování
    fetcher = LoggingVideoFetcher(fetcher)

    # První získání - z API
    print("\nPrvní získání:")
    video1 = fetcher.fetch("https://youtube.com/watch?v=123")

    # Druhé získání - z cache
    print("\nDruhé získání (z cache):")
    video2 = fetcher.fetch("https://youtube.com/watch?v=123")

    print("✅ Decoratory dynamicky přidaly cachování a logování!")


def demonstrate_chain_of_responsibility():
    """Demonstrace Chain of Responsibility Pattern."""
    print("\n" + "=" * 70)
    print("2. CHAIN OF RESPONSIBILITY - Řetězec Zpracovatelů")
    print("=" * 70)

    # Vytvořit řetězec
    spam_filter = SpamFilterHandler()
    priority_handler = PriorityHandler()
    content_handler = ContentHandler()

    spam_filter.set_next(priority_handler).set_next(content_handler)

    # Test různých požadavků
    print("\nTest 1: Normální obsah, nízká priorita")
    spam_filter.handle(Request("Dobrý obsah", priority=3))

    print("\nTest 2: Vysoká priorita")
    spam_filter.handle(Request("Důležitý obsah", priority=8))

    print("\nTest 3: Spam")
    spam_filter.handle(Request("Buy SPAM now!", priority=1))

    print("✅ Požadavky zpracovány řetězcem handlerů!")


def demonstrate_command():
    """Demonstrace Command Pattern."""
    print("\n" + "=" * 70)
    print("3. COMMAND PATTERN - Zapouzdření Požadavků")
    print("=" * 70)

    # Setup
    repository = IdeaRepository()
    invoker = CommandInvoker()

    # Vytvořit idea
    idea = IdeaInspiration(id="1", title="Python Tutorial")
    create_cmd = CreateIdeaCommand(repository, idea)

    print("\nProvádění příkazů:")
    invoker.execute(create_cmd)

    # Publikovat idea
    publish_cmd = PublishIdeaCommand(repository, "1")
    invoker.execute(publish_cmd)

    # Undo
    print("\nVracení zpět:")
    invoker.undo()  # Undo publish
    invoker.undo()  # Undo create

    print("✅ Příkazy provedeny a vráceny zpět!")


def demonstrate_state():
    """Demonstrace State Pattern."""
    print("\n" + "=" * 70)
    print("4. STATE PATTERN - Změna Chování podle Stavu")
    print("=" * 70)

    worker = Worker()

    print("\nZačátek úkolu:")
    worker.start_task()

    print("\nDokončení úkolu:")
    worker.complete_task()

    print("\nZačátek dalšího úkolu:")
    worker.start_task()

    print("\nSelhání úkolu:")
    worker.fail_task()

    print("\nRestart po selhání:")
    worker.start_task()

    print("✅ Worker mění chování podle stavu!")


def demonstrate_builder():
    """Demonstrace Builder Pattern."""
    print("\n" + "=" * 70)
    print("5. BUILDER PATTERN - Krok za Krokem Konstrukce")
    print("=" * 70)

    # Jednoduchý úkol
    print("\nJednoduchý úkol:")
    simple_task = VideoTaskBuilder("video-123").build()
    print(f"Vytvořen: {simple_task}")

    # Komplexní úkol
    print("\nKomplexní úkol:")
    complex_task = (
        VideoTaskBuilder("video-456")
        .with_title("Advanced Python Tutorial")
        .with_priority(9)
        .with_retry_count(5)
        .with_timeout(60)
        .add_metadata("source", "youtube")
        .add_metadata("duration", 1800)
        .build()
    )
    print(f"Vytvořen: {complex_task}")

    print("✅ Builder umožňuje flexibilní konstrukci objektů!")


def demonstrate_all():
    """Demonstrace všech rozšířených vzorů."""
    print("\n" + "=" * 70)
    print("ROZŠÍŘENÉ DESIGN PATTERNS PRO PRISMQ")
    print("=" * 70)

    demonstrate_decorator()
    demonstrate_chain_of_responsibility()
    demonstrate_command()
    demonstrate_state()
    demonstrate_builder()

    print("\n" + "=" * 70)
    print("KLÍČOVÉ PŘÍNOSY:")
    print("✅ Decorator: Dynamicky přidává funkčnost bez změny tříd")
    print("✅ Chain of Responsibility: Flexibilní zpracování požadavků")
    print("✅ Command: Zapouzdřuje operace, umožňuje undo/redo")
    print("✅ State: Mění chování objektu podle vnitřního stavu")
    print("✅ Builder: Umožňuje složitou konstrukci krok za krokem")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demonstrate_all()
