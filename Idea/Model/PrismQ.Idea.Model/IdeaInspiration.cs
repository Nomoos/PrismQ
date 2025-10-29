namespace PrismQ.Idea.Model;

/// <summary>
/// Represents a reference to an IdeaInspiration from the PrismQ.IdeaInspiration.Model.
/// This is a minimal representation used for establishing the M:N relationship.
/// The full IdeaInspiration model is defined in: https://github.com/Nomoos/PrismQ.IdeaInspiration.Model
/// </summary>
public class IdeaInspiration
{
    /// <summary>
    /// Gets or sets the unique identifier for the IdeaInspiration.
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// Gets or sets the collection of IdeaIdeaInspirations that link this IdeaInspiration to Ideas.
    /// This represents the many-to-many relationship.
    /// </summary>
    public ICollection<IdeaIdeaInspiration> IdeaIdeaInspirations { get; set; } = new List<IdeaIdeaInspiration>();
}
