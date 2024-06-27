import streamlit as st

@st.cache
def load_vocab(file_path) -> list:
    with open(file_path, 'r', encoding='utf-8') as f:
        vocab = f.read().splitlines()
        vocab.sort()
    # print(vocab[:10])
    return vocab


def levenshtein_distance(input_word, output_word):
    if (input_word, output_word) in st.session_state.distance_cache:
        return st.session_state.distance_cache[(input_word, output_word)]

    dp = [[0] * (len(output_word) + 1) for _ in range(len(input_word) + 1)]
    for i in range(len(input_word) + 1):
        dp[i][0] = i
    for j in range(len(output_word) + 1):
        dp[0][j] = j
    for i in range(1, len(input_word) + 1):
        for j in range(1, len(output_word) + 1):
            # if the last character is the same, no operation is needed
            if input_word[i - 1] == output_word[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            # else, adding, deleting, or replacing with cost 1 is considered
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1],
                               dp[i - 1][j - 1]) + 1
            st.session_state.distance_cache[(
                input_word[:i], output_word[:j])] = dp[i][j]
    return dp[-1][-1]


def get_levenstein_distances(input_word, vocab, k=5):
    distances = []
    for word in vocab:
        distances.append((word, levenshtein_distance(input_word, word)))
    distances.sort(key=lambda x: x[1])
    return distances[:k]


def choose_corrected_word(input_word_placeholder, output_text_placeholder, option_placeholders, buttons, suggestions):
    # Checck which button is clicked
    corrected_word = None
    for i, (_, button) in enumerate(buttons):
        if button:
            corrected_word = suggestions[i][0]
            break
    if corrected_word:
        print('Corrected word:', corrected_word)
        clear_elements([output_text_placeholder, *option_placeholders])
        st.session_state['last_word'] = corrected_word
        input_word_placeholder.empty()
        input_word_placeholder.text_input(
            'Input word', value=corrected_word)


def show_suggestions(output_text_placeholder, option_placeholders, buttons, suggestions):
    output_text_placeholder.write("*Did you mean...?*")
    for i, (word, _) in enumerate(suggestions):
        buttons.append(
            (option_placeholders[i], option_placeholders[i].button(word)))


def clear_elements(elements):
    for element in elements:
        element.empty()


def main():
    k = 5
    st.title('Word Correction using Levenshtein distance')
    vocab = load_vocab('./google-10000-english-usa.txt')
    if 'distance_cache' not in st.session_state:
        st.session_state.distance_cache = {}
    print('Empty input word 0')
    input_word_placeholder = st.empty()
    print('Empty input word 1')
    output_text_placeholder = st.empty()
    option_placeholders = [st.empty() for _ in range(k)]
    clear_placeholder = st.empty()
    buttons = []
    print('Last word 0:', st.session_state.get('last_word', None))
    input_word = input_word_placeholder.text_input('Input word')
    st.write(input_word)
    clear_button = clear_placeholder.button('Clear suggestions', type='primary',
                                            on_click=clear_elements,
                                            args=([*option_placeholders, output_text_placeholder],))
    if input_word and not clear_button:
        print('Input word:', input_word)
        print('Last word 1:', st.session_state.get('last_word', None))
        st.session_state['last_word'] = input_word
        print('Last word 2:', st.session_state.get('last_word', None))
        if input_word in vocab:
            st.write(f'Word *{input_word}* is correct')
        else:
            suggestions = get_levenstein_distances(input_word, vocab, k)
            show_suggestions(output_text_placeholder,
                             option_placeholders, buttons, suggestions)
            choose_corrected_word(input_word_placeholder,
                                  output_text_placeholder, option_placeholders, buttons, suggestions)


if __name__ == '__main__':
    main()
