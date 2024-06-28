import streamlit as st

st.set_page_config(page_title='Word Correction', page_icon=':writing_hand:', menu_items={
                   'About': "Made by [:rainbow[*tiviluson*] :sunglasses: :raccoon:](https://github.com/tiviluson) "})
st.title('Word Correction using Levenshtein distance')
st.logo('../assets/logo.png')
st.caption(
    'by [:rainbow[*tiviluson*] :sunglasses: :raccoon:](https://github.com/tiviluson) ')


@st.cache_data
def load_vocab(file_path) -> list:
    with open(file_path, 'r', encoding='utf-8') as f:
        vocab = f.read().splitlines()
        vocab.sort()
        print('Vocab loaded')
    return vocab


# Unuseful when cached with st.cache_data
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


def update_input(word, output_text_placeholder, option_placeholders):
    st.session_state.input_word = word
    clear_elements([output_text_placeholder, *option_placeholders])


def show_and_select_suggestions(output_text_placeholder, option_placeholders, buttons, suggestions):
    output_text_placeholder.write("*Did you mean...?*")
    for i, (word, _) in enumerate(suggestions):
        buttons.append((option_placeholders[i],
                        option_placeholders[i].button(word,
                                                      on_click=update_input,
                                                      args=(word, output_text_placeholder, option_placeholders))))


def clear_elements(elements):
    for element in elements:
        element.empty()


def init(num_of_suggestions):
    input_word_placeholder = st.empty()
    output_text_placeholder = st.empty()
    option_placeholders = [st.empty() for _ in range(num_of_suggestions)]
    clear_placeholder = st.empty()
    buttons = []
    input_word = input_word_placeholder.text_input(
        'Input word', key='input_word')
    clear_button = clear_placeholder.button('Clear suggestions', type='primary',
                                            on_click=clear_elements,
                                            args=([*option_placeholders, output_text_placeholder],))

    return output_text_placeholder, option_placeholders, buttons, input_word, clear_button


def main() -> None:
    num_of_suggestions = 5

    vocab = load_vocab('./google-10000-english-usa.txt')

    if 'distance_cache' not in st.session_state:
        st.session_state.distance_cache = {}

    output_text_placeholder, option_placeholders, buttons, input_word, clear_button = init(
        num_of_suggestions)
    if input_word and not clear_button:
        if input_word in vocab:
            st.write(f'Word *{input_word}* is correct')
        # If correction is needed
        else:
            suggestions = get_levenstein_distances(
                input_word, vocab, num_of_suggestions)
            show_and_select_suggestions(output_text_placeholder,
                                        option_placeholders, buttons, suggestions)


if __name__ == '__main__':
    main()
