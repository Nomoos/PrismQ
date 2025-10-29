namespace PrismQ.Idea.Model;

/// <summary>
/// Represents the many-to-many relationship between Idea and IdeaInspiration.
/// This is a junction/bridge entity that allows an Idea to be created from zero, one, or multiple IdeaInspirations.
/// </summary>
public class IdeaIdeaInspiration
{
    /// <summary>
    /// Gets or sets the unique identifier for the Idea.
    /// </summary>
    public Guid IdeaId { get; set; }

    /// <summary>
    /// Gets or sets the Idea navigation property.
    /// </summary>
    public Idea Idea { get; set; } = null!;

    /// <summary>
    /// Gets or sets the unique identifier for the IdeaInspiration.
    /// </summary>
    public Guid IdeaInspirationId { get; set; }

    /// <summary>
    /// Gets or sets the IdeaInspiration navigation property.
    /// </summary>
    public IdeaInspiration IdeaInspiration { get; set; } = null!;

    /// <summary>
    /// Gets or sets the date and time when this relationship was created.
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// Gets or sets an optional order or priority for how this IdeaInspiration contributes to the Idea.
    /// </summary>
    public int? Order { get; set; }
}
