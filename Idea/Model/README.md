# PrismQ.Idea.Model

A .NET model library for representing Ideas used in story generation within the PrismQ ecosystem.

## Overview

This library defines the `Idea` model and its many-to-many relationship with `IdeaInspiration` entities. An Idea represents a concept for generating a story and can be created from zero, one, or multiple IdeaInspirations.

## Models

### Idea
The main entity representing a story idea with the following properties:
- `Id` (Guid): Unique identifier
- `Title` (string): The title of the idea
- `Description` (string?): Optional detailed description
- `CreatedAt` (DateTime): Creation timestamp
- `UpdatedAt` (DateTime?): Last update timestamp
- `IdeaIdeaInspirations` (ICollection): Navigation property for the M:N relationship

### IdeaInspiration
A reference model for linking to IdeaInspiration entities from the [PrismQ.IdeaInspiration.Model](https://github.com/Nomoos/PrismQ.IdeaInspiration.Model) repository:
- `Id` (Guid): Unique identifier
- `IdeaIdeaInspirations` (ICollection): Navigation property for the M:N relationship

### IdeaIdeaInspiration
The junction entity that establishes the many-to-many relationship:
- `IdeaId` (Guid): Foreign key to Idea
- `IdeaInspirationId` (Guid): Foreign key to IdeaInspiration
- `Idea` (Idea): Navigation property to Idea
- `IdeaInspiration` (IdeaInspiration): Navigation property to IdeaInspiration
- `CreatedAt` (DateTime): When the relationship was created
- `Order` (int?): Optional ordering/priority for the inspiration

## Usage

```csharp
using PrismQ.Idea.Model;

// Create a new Idea
var idea = new Idea
{
    Id = Guid.NewGuid(),
    Title = "Epic Fantasy Adventure",
    Description = "A story about heroes on a quest",
    CreatedAt = DateTime.UtcNow
};

// Link to multiple IdeaInspirations
idea.IdeaIdeaInspirations.Add(new IdeaIdeaInspiration
{
    IdeaId = idea.Id,
    IdeaInspirationId = inspirationId1,
    CreatedAt = DateTime.UtcNow,
    Order = 1
});
```

## Building

```bash
dotnet build
```

## Target Framework

- .NET 8.0

## License

See LICENSE file in the repository.