namespace PrismQ.Idea.Model;

/// <summary>
/// Represents an Idea for generating a story.
/// An Idea can be created from zero, one, or multiple IdeaInspirations.
/// </summary>
public class Idea
{
    /// <summary>
    /// Gets or sets the unique identifier for the Idea.
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// Gets or sets the title of the Idea.
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the description of the Idea.
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// Gets or sets the date and time when the Idea was created.
    /// </summary>
    public DateTime CreatedAt { get; set; }

    /// <summary>
    /// Gets or sets the date and time when the Idea was last updated.
    /// </summary>
    public DateTime? UpdatedAt { get; set; }

    /// <summary>
    /// Gets or sets the collection of IdeaIdeaInspirations that link this Idea to IdeaInspirations.
    /// This represents the many-to-many relationship.
    /// </summary>
    public ICollection<IdeaIdeaInspiration> IdeaIdeaInspirations { get; set; } = new List<IdeaIdeaInspiration>();
}
