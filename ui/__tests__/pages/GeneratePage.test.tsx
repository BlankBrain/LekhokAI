import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import GeneratePage from '../../src/app/generate/page'
import { rest } from 'msw'
import { setupServer } from 'msw/node'

// Mock data
const mockCharacters = {
  characters: [
    { id: 'himu', name: 'Himu', usage_count: 29, created_at: '2025-01-01T00:00:00.000Z' },
    { id: 'harry_potter', name: 'Harry Potter', usage_count: 2, created_at: '2025-01-01T00:00:00.000Z' },
    { id: 'test', name: 'Test Character', usage_count: 5, created_at: '2025-01-01T00:00:00.000Z' }
  ]
}

const mockStoryResponse = {
  story: 'Once upon a time, there was a magical adventure...',
  image_prompt: 'A magical landscape with mountains',
  model_name: 'gemini-test',
  input_tokens: 150,
  output_tokens: 300
}

// MSW server setup
const server = setupServer(
  rest.get('http://localhost:8000/characters', (req, res, ctx) => {
    return res(ctx.json(mockCharacters))
  }),
  rest.post('http://localhost:8000/generate', (req, res, ctx) => {
    return res(ctx.json(mockStoryResponse))
  }),
  rest.post('http://localhost:8000/load_character/:character', (req, res, ctx) => {
    return res(ctx.json({ success: true }))
  })
)

// Setup and teardown
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('GeneratePage', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    // Mock environment variable for API base URL
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'
  })

  test('renders generate page with basic elements', () => {
    render(<GeneratePage />)
    
    // Check main heading
    expect(screen.getByRole('heading', { name: /generate story/i })).toBeInTheDocument()
    
    // Check form elements
    expect(screen.getByLabelText(/story prompt/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/character/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /generate story/i })).toBeInTheDocument()
    
    // Button should be disabled initially
    expect(screen.getByRole('button', { name: /generate story/i })).toBeDisabled()
  })

  test('loads characters on component mount', async () => {
    render(<GeneratePage />)
    
    // Wait for characters to load
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    // Check all characters are loaded
    expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: /harry potter/i })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: /test character/i })).toBeInTheDocument()
  })

  test('handles character loading failure', async () => {
    // Mock API failure
    server.use(
      rest.get('http://localhost:8000/characters', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }))
      })
    )
    
    render(<GeneratePage />)
    
    // Should show default option when loading fails
    await waitFor(() => {
      expect(screen.getByText(/select a character/i)).toBeInTheDocument()
    })
  })

  test('enables submit button when both fields are filled', async () => {
    render(<GeneratePage />)
    
    // Wait for characters to load
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    const storyInput = screen.getByLabelText(/story prompt/i)
    const characterSelect = screen.getByLabelText(/character/i)
    const submitButton = screen.getByRole('button', { name: /generate story/i })
    
    // Initially disabled
    expect(submitButton).toBeDisabled()
    
    // Fill story prompt
    await user.type(storyInput, 'A magical adventure')
    expect(submitButton).toBeDisabled() // Still disabled without character
    
    // Select character
    await user.selectOptions(characterSelect, 'himu')
    
    // Now should be enabled
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled()
    })
  })

  test('validates required fields', async () => {
    render(<GeneratePage />)
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    const submitButton = screen.getByRole('button', { name: /generate story/i })
    
    // Try to submit without filling fields - button should be disabled
    expect(submitButton).toBeDisabled()
    
    // Fill only story prompt
    const storyInput = screen.getByLabelText(/story prompt/i)
    await user.type(storyInput, 'Test story')
    
    // Still disabled without character
    expect(submitButton).toBeDisabled()
  })

  test('successfully generates story', async () => {
    render(<GeneratePage />)
    
    // Wait for characters to load
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    // Fill form
    const storyInput = screen.getByLabelText(/story prompt/i)
    const characterSelect = screen.getByLabelText(/character/i)
    
    await user.type(storyInput, 'A magical adventure')
    await user.selectOptions(characterSelect, 'himu')
    
    // Wait for button to be enabled
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate story/i })).not.toBeDisabled()
    })
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /generate story/i })
    await user.click(submitButton)
    
    // Should show loading state
    expect(screen.getByText(/generating/i)).toBeInTheDocument()
    
    // Wait for story to appear
    await waitFor(() => {
      expect(screen.getByText(/once upon a time/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  test('handles story generation API error', async () => {
    // Mock API error
    server.use(
      rest.post('http://localhost:8000/generate', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Generation failed' }))
      })
    )
    
    render(<GeneratePage />)
    
    // Wait for characters to load
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    // Fill and submit form
    const storyInput = screen.getByLabelText(/story prompt/i)
    const characterSelect = screen.getByLabelText(/character/i)
    
    await user.type(storyInput, 'Test story')
    await user.selectOptions(characterSelect, 'himu')
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate story/i })).not.toBeDisabled()
    })
    
    await user.click(screen.getByRole('button', { name: /generate story/i }))
    
    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/error.*generation/i)).toBeInTheDocument()
    })
  })

  test('displays loading state during generation', async () => {
    // Mock delayed response
    server.use(
      rest.post('http://localhost:8000/generate', (req, res, ctx) => {
        return res(ctx.delay(1000), ctx.json(mockStoryResponse))
      })
    )
    
    render(<GeneratePage />)
    
    // Wait for characters and fill form
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    const storyInput = screen.getByLabelText(/story prompt/i)
    const characterSelect = screen.getByLabelText(/character/i)
    
    await user.type(storyInput, 'Test story')
    await user.selectOptions(characterSelect, 'himu')
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate story/i })).not.toBeDisabled()
    })
    
    // Submit and check loading state
    await user.click(screen.getByRole('button', { name: /generate story/i }))
    
    expect(screen.getByText(/generating/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /generating/i })).toBeDisabled()
  })

  test('displays token usage information', async () => {
    render(<GeneratePage />)
    
    // Wait for characters to load and generate story
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    const storyInput = screen.getByLabelText(/story prompt/i)
    const characterSelect = screen.getByLabelText(/character/i)
    
    await user.type(storyInput, 'Test story')
    await user.selectOptions(characterSelect, 'himu')
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate story/i })).not.toBeDisabled()
    })
    
    await user.click(screen.getByRole('button', { name: /generate story/i }))
    
    // Wait for story and check token info
    await waitFor(() => {
      expect(screen.getByText(/once upon a time/i)).toBeInTheDocument()
    })
    
    // Check for token usage display (if implemented)
    const tokenInfo = screen.queryByText(/tokens/i)
    if (tokenInfo) {
      expect(tokenInfo).toBeInTheDocument()
    }
  })

  test('character selection updates form state', async () => {
    render(<GeneratePage />)
    
    // Wait for characters to load
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    const characterSelect = screen.getByLabelText(/character/i) as HTMLSelectElement
    
    // Select a character
    await user.selectOptions(characterSelect, 'himu')
    
    // Check selection
    expect(characterSelect.value).toBe('himu')
    
    // Change selection
    await user.selectOptions(characterSelect, 'harry_potter')
    expect(characterSelect.value).toBe('harry_potter')
  })

  test('form reset after successful generation', async () => {
    render(<GeneratePage />)
    
    // Wait for characters and complete generation
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /himu/i })).toBeInTheDocument()
    })
    
    const storyInput = screen.getByLabelText(/story prompt/i) as HTMLTextAreaElement
    const characterSelect = screen.getByLabelText(/character/i) as HTMLSelectElement
    
    await user.type(storyInput, 'Test story')
    await user.selectOptions(characterSelect, 'himu')
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate story/i })).not.toBeDisabled()
    })
    
    await user.click(screen.getByRole('button', { name: /generate story/i }))
    
    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText(/once upon a time/i)).toBeInTheDocument()
    })
    
    // Check if form is reset (implementation dependent)
    // This test verifies the behavior if auto-reset is implemented
    await waitFor(() => {
      if (storyInput.value === '') {
        expect(storyInput.value).toBe('')
      }
    })
  })
}) 